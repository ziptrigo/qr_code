from __future__ import annotations

from datetime import UTC, datetime, timedelta

from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string


class PasswordResetToken(models.Model):
    """Time-limited token to allow a user to reset their password."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Password reset token'
        verbose_name_plural = 'Password reset tokens'

    def __str__(self) -> str:  # pragma: no cover - representation only
        return f'PasswordResetToken(user={self.user_id}, token={self.token})'

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        ttl_hours = getattr(settings, 'PASSWORD_RESET_TOKEN_TTL_HOURS', 4)
        expires_at = self.created_at + timedelta(hours=ttl_hours)
        return datetime.now(UTC) >= expires_at

    @classmethod
    def create_for_user(cls, user: 'User') -> 'PasswordResetToken':
        """Create and return a new token for the given user."""

        # 48 characters of URL-safe randomness is plenty.
        token = get_random_string(48)
        return cls.objects.create(user=user, token=token)
