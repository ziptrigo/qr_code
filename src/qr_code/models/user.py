from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with additional fields."""

    name = models.CharField(max_length=255, help_text='User full name')
    email = models.EmailField(unique=True, help_text='User email address')
    email_confirmed = models.BooleanField(default=False, help_text='Whether email is confirmed')
    email_confirmed_at = models.DateTimeField(
        null=True, blank=True, help_text='When email was confirmed'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return f'{self.email} - {self.name}'
