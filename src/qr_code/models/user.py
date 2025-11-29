from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with additional fields."""

    name = models.CharField(max_length=255, help_text='User full name')
    email = models.EmailField(unique=True, help_text='User email address')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return f'{self.email} - {self.name}'
