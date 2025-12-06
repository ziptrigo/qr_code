from datetime import UTC, datetime, timedelta
from typing import Self

from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string

from .user import User


class TimeLimitedToken(models.Model):
    """Time-limited token for various user actions (password reset, email confirmation, etc.)."""

    TOKEN_TYPE_PASSWORD_RESET = 'password_reset'
    TOKEN_TYPE_EMAIL_CONFIRMATION = 'email_confirmation'

    TOKEN_TYPE_CHOICES = [
        (TOKEN_TYPE_PASSWORD_RESET, 'Password Reset'),
        (TOKEN_TYPE_EMAIL_CONFIRMATION, 'Email Confirmation'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='time_limited_tokens',
    )
    token = models.CharField(max_length=64, unique=True)
    token_type = models.CharField(max_length=32, choices=TOKEN_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Time-limited token'
        verbose_name_plural = 'Time-limited tokens'
        indexes = [
            models.Index(fields=['token', 'token_type']),
        ]

    def __str__(self) -> str:  # pragma: no cover - representation only
        return f'TimeLimitedToken(user={self.user_id}, type={self.token_type}, token={self.token})'  # type: ignore

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        if self.token_type == self.TOKEN_TYPE_PASSWORD_RESET:
            ttl_hours = getattr(settings, 'PASSWORD_RESET_TOKEN_TTL_HOURS', 4)
        elif self.token_type == self.TOKEN_TYPE_EMAIL_CONFIRMATION:
            ttl_hours = getattr(settings, 'EMAIL_CONFIRMATION_TOKEN_TTL_HOURS', 48)
        else:
            ttl_hours = 4  # Default fallback
        expires_at = self.created_at + timedelta(hours=ttl_hours)
        return datetime.now(UTC) >= expires_at

    @classmethod
    def create_for_user(cls, user: User, token_type: str) -> Self:
        """Create and return a new token for the given user and type."""

        # 48 characters of URL-safe randomness is plenty.
        token = get_random_string(48)
        return cls.objects.create(user=user, token=token, token_type=token_type)  # type: ignore
