"""
Integration tests to verify setup and end-to-end functionality.
"""

import pytest
from django.contrib.auth.models import User
from qrcodes.models import QRCode
from qrcodes.services import QRCodeGenerator


@pytest.mark.django_db
@pytest.mark.integration
class TestSetupIntegration:
    """Test end-to-end setup and functionality."""
    
    def test_complete_qr_generation_workflow(self):
        """Test the complete workflow of QR code generation."""
        # Create user
        user = User.objects.create_user(
            username='setuptest',
            email='setup@example.com',
            password='testpass123'
        )
        
        # Create QR code
        qr = QRCode.objects.create(
            content='https://example.com',
            created_by=user,
            qr_format='png',
            size=10,
            error_correction='M',
            border=4,
            background_color='white',
            foreground_color='black',
            image_file='temp.png'
        )
        
        assert qr.content == 'https://example.com'
        assert qr.created_by == user
        
        # Generate QR code image
        image_path = QRCodeGenerator.generate_qr_code(qr)
        qr.image_file = image_path
        qr.save()
        
        assert qr.image_file is not None
        assert '.png' in qr.image_file
    
    def test_url_shortening_workflow(self):
        """Test URL shortening end-to-end."""
        # Create user
        user = User.objects.create_user(
            username='shorttest',
            email='short@example.com',
            password='testpass123'
        )
        
        # Create QR code with URL shortening
        qr = QRCode.objects.create(
            content='https://example.com/very-long-url',
            original_url='https://example.com/very-long-url',
            use_url_shortening=True,
            created_by=user,
            qr_format='svg',
            image_file='temp.svg'
        )
        
        assert qr.short_code is not None
        assert len(qr.short_code) == 8
        
        redirect_url = qr.get_redirect_url()
        assert redirect_url is not None
        assert qr.short_code in redirect_url
        
        # Update content to shortened URL
        qr.content = redirect_url
        image_path = QRCodeGenerator.generate_qr_code(qr)
        qr.image_file = image_path
        qr.save()
        
        assert qr.image_file is not None
        assert '.svg' in qr.image_file
    
    def test_scan_tracking_workflow(self):
        """Test scan tracking functionality."""
        user = User.objects.create_user(
            username='scantest',
            password='testpass123'
        )
        
        qr = QRCode.objects.create(
            content='https://example.com',
            use_url_shortening=True,
            created_by=user,
            image_file='test.png'
        )
        
        assert qr.scan_count == 0
        assert qr.last_scanned_at is None
        
        # Simulate scans
        for i in range(3):
            qr.increment_scan_count()
        
        assert qr.scan_count == 3
        assert qr.last_scanned_at is not None
