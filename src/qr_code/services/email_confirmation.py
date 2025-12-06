from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from django.conf import settings
from django.urls import reverse
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..models.time_limited_token import TimeLimitedToken
from ..models.user import User
from .email_service import EmailBackend, get_email_backend


@dataclass(slots=True)
class EmailConfirmationService:
    """High-level operations for email confirmation flow."""

    email_backend: EmailBackend

    def send_confirmation_email(self, user: User) -> None:
        """Create a confirmation token for the user and send confirmation email."""

        token = TimeLimitedToken.create_for_user(
            user, TimeLimitedToken.TOKEN_TYPE_EMAIL_CONFIRMATION
        )
        confirmation_url = self._build_confirmation_url(token.token)
        subject, text_body, html_body = render_email_confirmation_email(
            user=user,
            confirmation_url=confirmation_url,
        )
        self.email_backend.send_email(user.email, subject, text_body, html_body)

    def _build_confirmation_url(self, token: str) -> str:
        base = settings.QR_CODE_BASE_URL.rstrip('/')
        path = reverse('confirm-email-page', args=[token])
        return f'{base}{path}'

    @staticmethod
    def validate_token(token: str) -> TimeLimitedToken | None:
        """Validate a confirmation token and return it if valid."""

        try:
            tlt: TimeLimitedToken = TimeLimitedToken.objects.get(
                token=token, token_type=TimeLimitedToken.TOKEN_TYPE_EMAIL_CONFIRMATION
            )  # type: ignore
        except TimeLimitedToken.DoesNotExist:
            return None

        if tlt.is_used or tlt.is_expired:
            return None
        return tlt

    @staticmethod
    def confirm_email(token: TimeLimitedToken) -> None:
        """Mark the user's email as confirmed and the token as used."""

        user = token.user
        user.email_confirmed = True
        user.email_confirmed_at = datetime.now(UTC)
        user.save(update_fields=['email_confirmed', 'email_confirmed_at'])

        token.used_at = datetime.now(UTC)
        token.save(update_fields=['used_at'])


def get_email_confirmation_service() -> EmailConfirmationService:
    return EmailConfirmationService(email_backend=get_email_backend())


def render_email_confirmation_email(*, user: User, confirmation_url: str) -> tuple[str, str, str]:
    """Render email subject, text, and HTML body for a confirmation email using Jinja2.

    Template: ``src/qr_code/static/emails/email_validation.j2``.
    """

    base_dir = Path(settings.BASE_DIR)
    template_path = base_dir / 'src' / 'qr_code' / 'static' / 'emails'

    env = Environment(
        loader=FileSystemLoader(str(template_path)),
        autoescape=select_autoescape(['html', 'xml']),
    )
    template = env.get_template('email_validation.j2')

    rendered = template.render(
        user=user,
        confirmation_url=confirmation_url,
        ttl_hours=settings.EMAIL_CONFIRMATION_TOKEN_TTL_HOURS,
    )

    # The template is structured as three sections one after another:
    # subject (first line), then text body, then HTML body.
    lines = [line for line in rendered.splitlines() if not line.strip().startswith('{#')]

    # Subject: first non-empty line.
    non_empty = [line for line in lines if line.strip()]
    subject = non_empty[0] if non_empty else 'Confirm your QR Code account email'

    # Heuristically split into text and HTML by blank line before first '<p>' or '<' tag.
    joined = '\\n'.join(non_empty[1:])
    marker = '<p>'
    idx = joined.find(marker)
    if idx == -1:
        text_body = joined.strip()
        html_body = f'<pre>{text_body}</pre>' if text_body else ''
    else:
        text_body = joined[:idx].strip()
        html_body = joined[idx:].strip()

    return subject, text_body, html_body
