"""
Pytest configuration and fixtures for the QR code project.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from src.models import QRCode

User = get_user_model()


@pytest.fixture
def api_client():
    """Provide an API client for testing."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser@example.com',
        email='testuser@example.com',
        password='testpass123',
        name='Test User',
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Provide an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def qr_code(user):
    """Create a test QR code."""
    return QRCode.objects.create(
        content='https://example.com',
        created_by=user,
        qr_format='png',
        size=10,
        error_correction='M',
        border=4,
        background_color='white',
        foreground_color='black',
        image_file='test.png',
    )


@pytest.fixture
def qr_code_with_shortening(user):
    """Create a test QR code with URL shortening."""
    return QRCode.objects.create(
        content='https://example.com/long-url',
        original_url='https://example.com/long-url',
        use_url_shortening=True,
        created_by=user,
        qr_format='png',
        image_file='test_short.png',
    )
