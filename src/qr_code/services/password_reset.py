from dataclasses import dataclass

from django.conf import settings
from django.urls import reverse
from jinja2 import Environment, FileSystemLoader, select_autoescape

# TODO: Rewrite to use JWT tokens instead of TimeLimitedToken
# from ..models.time_limited_token import TimeLimitedToken
from ..models.user import User
from .email_service import EmailBackendClass, get_email_backend, send_email


@dataclass(slots=True)
class PasswordResetService:
    """High-level operations for password reset flow."""

    email_backend_classes: list[EmailBackendClass]

    def request_reset(self, email: str):
        """Create a reset token for the user with the given email and send email.

        If the user does not exist, this method does nothing. This keeps behavior
        indistinguishable from the caller's perspective.
        """

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        # TODO: Generate JWT token for password reset
        # prt = TimeLimitedToken.create_for_user(user, TimeLimitedToken.TOKEN_TYPE_PASSWORD_RESET)
        # reset_url = self._build_reset_url(prt.token)
        reset_url = self._build_reset_url('TODO')
        subject, text_body, html_body = render_password_reset_email(
            user=user,
            reset_url=reset_url,
        )
        send_email(
            to=user.email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            backend_classes=self.email_backend_classes,
        )

    def _build_reset_url(self, token: str) -> str:
        base = settings.BASE_URL.rstrip('/')
        path = reverse('reset-password-page', args=[token])
        return f'{base}{path}'

    @staticmethod
    def validate_token(token: str) -> User | None:  # type: ignore[return]
        # TODO: Validate JWT token and return user
        return None

    @staticmethod
    def mark_used(user: User):  # type: ignore[override]
        # TODO: JWT tokens don't need to be marked as used
        pass


def get_password_reset_service() -> PasswordResetService:
    return PasswordResetService(email_backend_classes=get_email_backend())


def render_password_reset_email(*, user: User, reset_url: str) -> tuple[str, str, str]:
    """Render email subject, text, and HTML body for a reset email using Jinja2.

    Template: ``src/qr_code/static/emails/password_reset.j2``.
    """

    template_path = settings.PROJECT_ROOT / 'src' / 'qr_code' / 'static' / 'emails'

    env = Environment(
        loader=FileSystemLoader(str(template_path)),
        autoescape=select_autoescape(['html', 'xml']),
    )
    template = env.get_template('password_reset.j2')

    rendered = template.render(
        user=user,
        reset_url=reset_url,
        ttl_hours=settings.PASSWORD_RESET_TOKEN_TTL_HOURS,
    )

    # The template is structured as three sections one after another:
    # subject (first line), then text body, then HTML body.
    lines = [line for line in rendered.splitlines() if not line.strip().startswith('{#')]

    # Subject: first non-empty line.
    non_empty = [line for line in lines if line.strip()]
    subject = non_empty[0] if non_empty else 'Reset your QR Code account password'

    # Heuristically split into text and HTML by blank line before first '<p>' or '<' tag.
    joined = '\n'.join(non_empty[1:])
    marker = '<p>'
    idx = joined.find(marker)
    if idx == -1:
        text_body = joined.strip()
        html_body = f'<pre>{text_body}</pre>' if text_body else ''
    else:
        text_body = joined[:idx].strip()
        html_body = joined[idx:].strip()

    return subject, text_body, html_body
