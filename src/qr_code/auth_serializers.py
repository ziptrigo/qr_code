import re
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from rest_framework import serializers

if TYPE_CHECKING:  # Use a proper type for static analysis only.
    from .models import User as UserType
else:
    UserType = AbstractBaseUser

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    """Serializer for user signup."""

    name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Password must be at least 6 characters and contain at least one digit',
    )

    def validate_password(self, value: str) -> str:
        """Validate password strength: minimum 6 chars and at least one digit."""
        if len(value) < 6:
            raise serializers.ValidationError('Password must be at least 6 characters long.')
        if not re.search(r'\d', value):
            raise serializers.ValidationError('Password must contain at least one digit.')
        return value

    def validate_email(self, value: str) -> str:
        """Check if email already exists."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with that email already exists.')
        return value

    def create(self, validated_data: dict) -> UserType:
        """Create and return a new user."""
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
