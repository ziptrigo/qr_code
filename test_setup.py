#!python
"""
Quick test script to verify the QR code service is working correctly.
Run this after setting up the project to ensure everything is configured properly.
"""

import os
import sys

import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# E402: module level import not at top of file
from django.contrib.auth.models import User  # noqa: E402

from src.models import QRCode  # noqa: E402
from src.services import QRCodeGenerator  # noqa: E402


def test_model_creation():
    """Test that we can create a QRCode model instance."""
    print('Testing model creation...')

    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser', defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print('✓ Created test user')
    else:
        print('✓ Test user already exists')

    return user


def test_qr_generation(user):
    """Test QR code generation."""
    print('\nTesting QR code generation...')

    # Create a simple QR code
    qr = QRCode.objects.create(
        content='https://example.com',
        created_by=user,
        qr_format='png',
        size=10,
        error_correction='M',
        border=4,
        background_color='white',
        foreground_color='black',
        image_file='temp.png',  # Will be replaced
    )

    print(f'✓ Created QRCode instance: {qr.id}')

    # Generate the actual QR code image
    try:
        image_path = QRCodeGenerator.generate_qr_code(qr)
        qr.image_file = image_path
        qr.save()
        print(f'✓ Generated QR code image: {image_path}')
    except Exception as e:
        print(f'✗ Failed to generate QR code: {e}')
        return False

    return qr


def test_url_shortening(user):
    """Test URL shortening functionality."""
    print('\nTesting URL shortening...')

    qr = QRCode.objects.create(
        content='https://example.com/very-long-url',
        original_url='https://example.com/very-long-url',
        use_url_shortening=True,
        created_by=user,
        qr_format='svg',
        image_file='temp.svg',
    )

    if qr.short_code:
        print(f'✓ Generated short code: {qr.short_code}')
        redirect_url = qr.get_redirect_url()
        print(f'✓ Redirect URL: {redirect_url}')

        # Generate QR code with shortened URL
        if redirect_url:
            qr.content = redirect_url
            image_path = QRCodeGenerator.generate_qr_code(qr)
            qr.image_file = image_path
            qr.save()
            print('✓ Generated QR code with shortened URL')
        return True
    else:
        print('✗ Failed to generate short code')
        return False


def test_scan_tracking():
    """Test scan tracking."""
    print('\nTesting scan tracking...')

    qr = QRCode.objects.filter(short_code__isnull=False).first()
    if not qr:
        print('⚠ No QR codes with short codes to test')
        return True

    initial_count = qr.scan_count
    qr.increment_scan_count()
    qr.refresh_from_db()

    if qr.scan_count == initial_count + 1:
        print(f'✓ Scan count incremented: {initial_count} → {qr.scan_count}')
        return True
    else:
        print('✗ Scan count not incremented properly')
        return False


def run_tests():
    """Run all tests."""
    print('=' * 60)
    print('QR Code Service Setup Test')
    print('=' * 60)

    try:
        user = test_model_creation()
        qr = test_qr_generation(user)

        if qr:
            success = test_url_shortening(user)
            success = test_scan_tracking() and success

            print('\n' + '=' * 60)
            if success:
                print('✓ All tests passed!')
                print('=' * 60)
                print('\nYour QR code service is ready to use!')
                print('\nGenerated QR codes can be found in: media/qrcodes/')
                print('\nNext steps:')
                print('1. Run: python manage.py createsuperuser')
                print('2. Start server: python manage.py runserver')
                print('3. Visit: http://localhost:8000/admin/')
            else:
                print('✗ Some tests failed')
                print('=' * 60)
                return 1
        else:
            print('\n✗ QR code generation failed')
            return 1

    except Exception as e:
        print(f'\n✗ Error during testing: {e}')
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(run_tests())
