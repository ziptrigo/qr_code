from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.urls import reverse
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..models.password_reset_token import PasswordResetToken
from ..models.user import User
from .email_service import EmailBackend, get_email_backend


@dataclass(slots=True)
class PasswordResetService:
    """High-level operations for password reset flow."""

    email_backend: EmailBackend

    def request_reset(self, email: str) -> None:
        """Create a reset token for the user with the given email and send email.

        If the user does not exist, this method does nothing. This keeps behavior
        indistinguishable from the caller's perspective.
        """

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        prt = PasswordResetToken.create_for_user(user)
        reset_url = self._build_reset_url(prt.token)
        subject, text_body, html_body = render_password_reset_email(
            user=user,
            reset_url=reset_url,
        )
        self.email_backend.send_email(user.email, subject, text_body, html_body)

    def _build_reset_url(self, token: str) -> str:
        base = settings.QR_CODE_BASE_URL.rstrip("/")
        path = reverse("reset-password-page", args=[token])
        return f"{base}{path}"

    @staticmethod
    def validate_token(token: str) -> PasswordResetToken | None:
        from typing import cast

        try:
            prt = cast(
                PasswordResetToken,
                PasswordResetToken.objects.get(token=token),
            )
        except PasswordResetToken.DoesNotExist:
            return None

        if prt.is_used or prt.is_expired:
            return None
        return prt

    @staticmethod
    def mark_used(prt: PasswordResetToken) -> None:
        from datetime import UTC, datetime

        prt.used_at = datetime.now(UTC)
        prt.save(update_fields=["used_at"])


def get_password_reset_service() -> PasswordResetService:
    return PasswordResetService(email_backend=get_email_backend())


def render_password_reset_email(*, user: User, reset_url: str) -> tuple[str, str, str]:
    """Render email subject, text, and HTML body for a reset email using Jinja2.

    Template: ``src/qr_code/static/emails/password_reset.j2``.
    """

    base_dir = Path(settings.BASE_DIR)
    template_path = base_dir / 'src' / 'qr_code' / 'static' / 'emails'

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
