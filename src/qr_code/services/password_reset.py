from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings
from django.urls import reverse

from ..models.user import PasswordResetToken, User
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
        try:
            prt = PasswordResetToken.objects.get(token=token)
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
    """Render email subject, text, and HTML body for a reset email."""

    subject = "Reset your QR Code account password"
    text_body = (
        "You requested a password reset for your QR Code account.\n\n"
        f"Click the link below to set a new password (valid for "
        f"{settings.PASSWORD_RESET_TOKEN_TTL_HOURS} hours):\n{reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )
    html_body = (
        "<p>You requested a password reset for your QR Code account.</p>"
        f"<p>Click the link below to set a new password (valid for "
        f"{settings.PASSWORD_RESET_TOKEN_TTL_HOURS} hours):</p>"
        f'<p><a href="{reset_url}">{reset_url}</a></p>'
        "<p>If you did not request this, you can ignore this email.</p>"
    )
    return subject, text_body, html_body
