"""
Integration tests for QR code API endpoints.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from src.qr_code.models import QRCode

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.integration
class TestQRCodeAPI:
    """Test cases for QRCode API endpoints."""

    def test_create_qrcode_with_url(self, authenticated_client):
        """Test creating a QR code with a URL."""
        url = reverse('qrcode-list')
        data = {
            'url': 'https://example.com',
            'qr_format': 'png',
            'size': 10,
            'error_correction': 'M',
        }

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert QRCode.objects.filter(id=response.data['id']).exists()

    def test_create_qrcode_with_data(self, authenticated_client):
        """Test creating a QR code with custom data."""
        url = reverse('qrcode-list')
        data = {'data': 'Hello World!', 'qr_format': 'svg', 'size': 15}

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        qr = QRCode.objects.get(id=response.data['id'])
        assert qr.content == 'Hello World!'

    def test_create_qrcode_with_non_url_text_in_url_field(self, authenticated_client):
        """Test creating a QR code when arbitrary text is sent via the url field."""
        endpoint = reverse('qrcode-list')
        payload = {
            'url': 'Just some text, not a URL',
            'qr_format': 'png',
        }

        response = authenticated_client.post(endpoint, payload, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        qr = QRCode.objects.get(id=response.data['id'])
        assert qr.content == 'Just some text, not a URL'
        assert qr.original_url == 'Just some text, not a URL'

    def test_create_qrcode_with_url_shortening(self, authenticated_client):
        """Test creating a QR code with URL shortening."""
        url = reverse('qrcode-list')
        data = {
            'url': 'https://example.com/very/long/url',
            'use_url_shortening': True,
            'qr_format': 'png',
        }

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        qr = QRCode.objects.get(id=response.data['id'])
        assert qr.use_url_shortening is True
        assert qr.short_code is not None
        assert qr.original_url == 'https://example.com/very/long/url'

    def test_create_qrcode_requires_authentication(self, api_client):
        """Test that creating QR code requires authentication."""
        url = reverse('qrcode-list')
        data = {'url': 'https://example.com'}

        response = api_client.post(url, data, format='json')

        # Session auth may return 403 (CSRF) or 401 (no session)
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_create_qrcode_missing_data(self, authenticated_client):
        """Test creating QR code without url or data fails."""
        url = reverse('qrcode-list')
        data = {'qr_format': 'png'}

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_qrcode_both_url_and_data(self, authenticated_client):
        """Test creating QR code with both url and data fails."""
        url = reverse('qrcode-list')
        data = {'url': 'https://example.com', 'data': 'Some data'}

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_qrcodes(self, authenticated_client, qr_code):
        """Test listing QR codes."""
        url = reverse('qrcode-list')

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_list_qrcodes_filtered_by_user(self, authenticated_client, user):
        """Test that users only see their own QR codes."""
        # Create QR code for current user
        QRCode.objects.create(content='https://user1.com', created_by=user, image_file='user1.png')

        # Create another user and their QR code
        other_user = User.objects.create_user(
            username='otheruser@example.com',
            email='otheruser@example.com',
            password='otherpass',
            name='Other User',
        )
        QRCode.objects.create(
            content='https://user2.com', created_by=other_user, image_file='user2.png'
        )

        url = reverse('qrcode-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Should only see own QR codes
        for qr in response.data:
            qr_obj = QRCode.objects.get(id=qr['id'])
            assert qr_obj.created_by == user

    def test_retrieve_qrcode(self, authenticated_client, qr_code):
        """Test retrieving a specific QR code."""
        url = reverse('qrcode-detail', kwargs={'pk': qr_code.id})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(qr_code.id)
        assert response.data['content'] == qr_code.content
        assert 'image_url' in response.data

    def test_delete_qrcode(self, authenticated_client, qr_code):
        """Test deleting a QR code."""
        url = reverse('qrcode-detail', kwargs={'pk': qr_code.id})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not QRCode.objects.filter(id=qr_code.id).exists()

    def test_create_with_custom_colors(self, authenticated_client):
        """Test creating QR code with custom colors."""
        url = reverse('qrcode-list')
        data = {
            'url': 'https://example.com',
            'background_color': 'transparent',
            'foreground_color': '#0000FF',
            'qr_format': 'png',
        }

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        qr = QRCode.objects.get(id=response.data['id'])
        assert qr.background_color == 'transparent'
        assert qr.foreground_color == '#0000FF'

    def test_create_with_all_formats(self, authenticated_client):
        """Test creating QR codes with all supported formats."""
        formats = ['png', 'svg', 'pdf']

        for fmt in formats:
            url = reverse('qrcode-list')
            data = {'url': f'https://example.com/{fmt}', 'qr_format': fmt}

            response = authenticated_client.post(url, data, format='json')

            assert response.status_code == status.HTTP_201_CREATED
            qr = QRCode.objects.get(id=response.data['id'])
            assert qr.qr_format == fmt

    def test_update_qrcode_name(self, authenticated_client, qr_code):
        """Test updating a QR code name."""
        url = reverse('qrcode-detail', kwargs={'pk': qr_code.id})
        data = {'name': 'Updated QR Code Name'}

        response = authenticated_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        qr_code.refresh_from_db()
        assert qr_code.name == 'Updated QR Code Name'

    def test_update_qrcode_name_only(self, authenticated_client, qr_code):
        """Test that only the name field can be updated, other fields are ignored."""
        url = reverse('qrcode-detail', kwargs={'pk': qr_code.id})
        original_content = qr_code.content
        original_format = qr_code.qr_format
        data = {
            'name': 'New Name',
            'content': 'Should be ignored',
            'qr_format': 'svg',  # Try to change format
        }

        response = authenticated_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        qr_code.refresh_from_db()
        assert qr_code.name == 'New Name'
        assert qr_code.content == original_content  # Should not change
        assert qr_code.qr_format == original_format  # Should not change

    def test_update_qrcode_not_owned(self, authenticated_client, user):
        """Test that users cannot update QR codes they don't own."""
        # Create another user and their QR code
        other_user = User.objects.create_user(
            username='otheruser@example.com',
            email='otheruser@example.com',
            password='otherpass',
            name='Other User',
        )
        other_qr = QRCode.objects.create(
            content='https://other.com', created_by=other_user, image_file='other.png'
        )

        url = reverse('qrcode-detail', kwargs={'pk': other_qr.id})
        data = {'name': 'Hacked Name'}

        response = authenticated_client.put(url, data, format='json')

        # Should return 404 (not found) because get_queryset filters by user
        assert response.status_code == status.HTTP_404_NOT_FOUND
        other_qr.refresh_from_db()
        assert other_qr.name != 'Hacked Name'

    def test_update_qrcode_empty_name(self, authenticated_client, qr_code):
        """Test updating QR code with empty name fails validation."""
        url = reverse('qrcode-detail', kwargs={'pk': qr_code.id})
        data = {'name': ''}

        response = authenticated_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_partial_update_qrcode(self, authenticated_client, qr_code):
        """Test partial update (PATCH) of QR code name."""
        url = reverse('qrcode-detail', kwargs={'pk': qr_code.id})
        data = {'name': 'Patched Name'}

        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        qr_code.refresh_from_db()
        assert qr_code.name == 'Patched Name'


@pytest.mark.django_db
@pytest.mark.integration
class TestRedirectEndpoint:
    """Test cases for the redirect endpoint."""

    def test_redirect_with_valid_short_code(self, api_client, qr_code_with_shortening):
        """Test redirecting with a valid short code."""
        url = reverse('qrcode-redirect', kwargs={'short_code': qr_code_with_shortening.short_code})

        response = api_client.get(url, follow=False)

        assert response.status_code == status.HTTP_302_FOUND
        assert response.url == qr_code_with_shortening.original_url

    def test_redirect_increments_scan_count(self, api_client, qr_code_with_shortening):
        """Test that redirect increments scan count."""
        initial_count = qr_code_with_shortening.scan_count

        url = reverse('qrcode-redirect', kwargs={'short_code': qr_code_with_shortening.short_code})
        api_client.get(url)

        qr_code_with_shortening.refresh_from_db()
        assert qr_code_with_shortening.scan_count == initial_count + 1
        assert qr_code_with_shortening.last_scanned_at is not None

    def test_redirect_with_invalid_short_code(self, api_client):
        """Test redirecting with an invalid short code."""
        url = reverse('qrcode-redirect', kwargs={'short_code': 'invalid'})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_redirect_public_access(self, api_client, qr_code_with_shortening):
        """Test that redirect endpoint doesn't require authentication."""
        url = reverse('qrcode-redirect', kwargs={'short_code': qr_code_with_shortening.short_code})

        # Should work without authentication
        response = api_client.get(url, follow=False)

        assert response.status_code == status.HTTP_302_FOUND
