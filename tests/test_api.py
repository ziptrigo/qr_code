"""
Integration tests for QR code API endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from src.models import QRCode


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
            'error_correction': 'M'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert QRCode.objects.filter(id=response.data['id']).exists()
    
    def test_create_qrcode_with_data(self, authenticated_client):
        """Test creating a QR code with custom data."""
        url = reverse('qrcode-list')
        data = {
            'data': 'Hello World!',
            'qr_format': 'svg',
            'size': 15
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        qr = QRCode.objects.get(id=response.data['id'])
        assert qr.content == 'Hello World!'
    
    def test_create_qrcode_with_url_shortening(self, authenticated_client):
        """Test creating a QR code with URL shortening."""
        url = reverse('qrcode-list')
        data = {
            'url': 'https://example.com/very/long/url',
            'use_url_shortening': True,
            'qr_format': 'png'
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
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_qrcode_missing_data(self, authenticated_client):
        """Test creating QR code without url or data fails."""
        url = reverse('qrcode-list')
        data = {'qr_format': 'png'}
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_qrcode_both_url_and_data(self, authenticated_client):
        """Test creating QR code with both url and data fails."""
        url = reverse('qrcode-list')
        data = {
            'url': 'https://example.com',
            'data': 'Some data'
        }
        
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
        QRCode.objects.create(
            content='https://user1.com',
            created_by=user,
            image_file='user1.png'
        )
        
        # Create another user and their QR code
        from django.contrib.auth.models import User
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass'
        )
        QRCode.objects.create(
            content='https://user2.com',
            created_by=other_user,
            image_file='user2.png'
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
            'qr_format': 'png'
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
            data = {
                'url': f'https://example.com/{fmt}',
                'qr_format': fmt
            }
            
            response = authenticated_client.post(url, data, format='json')
            
            assert response.status_code == status.HTTP_201_CREATED
            qr = QRCode.objects.get(id=response.data['id'])
            assert qr.qr_format == fmt


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


@pytest.mark.django_db
@pytest.mark.integration
class TestJWTAuthentication:
    """Test cases for JWT authentication."""
    
    def test_obtain_token_with_valid_credentials(self, api_client, user):
        """Test obtaining JWT token with valid credentials."""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_obtain_token_with_invalid_credentials(self, api_client):
        """Test obtaining JWT token with invalid credentials."""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token(self, api_client, user):
        """Test refreshing JWT token."""
        # First obtain token
        obtain_url = reverse('token_obtain_pair')
        obtain_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        obtain_response = api_client.post(obtain_url, obtain_data, format='json')
        refresh_token = obtain_response.data['refresh']
        
        # Now refresh it
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': refresh_token}
        
        response = api_client.post(refresh_url, refresh_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
