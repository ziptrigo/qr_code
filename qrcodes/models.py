from django.db import models
from django.contrib.auth.models import User
import uuid
import string
import random


def generate_short_code(length=8):
    """Generate a random short code for URL shortening."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


class QRCode(models.Model):
    """Model to store QR code data and settings."""
    
    FORMAT_CHOICES = [
        ('png', 'PNG'),
        ('svg', 'SVG'),
        ('jpeg', 'JPEG'),
    ]
    
    ERROR_CORRECTION_CHOICES = [
        ('L', 'Low (~7%)'),
        ('M', 'Medium (~15%)'),
        ('Q', 'Quartile (~25%)'),
        ('H', 'High (~30%)'),
    ]
    
    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qrcodes')
    
    # QR Code content and settings
    content = models.TextField(help_text="The actual content encoded in the QR code")
    original_url = models.URLField(max_length=2000, null=True, blank=True, 
                                   help_text="Original URL if content is a shortened URL")
    use_url_shortening = models.BooleanField(default=False, 
                                             help_text="Whether to use URL shortening")
    short_code = models.CharField(max_length=16, unique=True, null=True, blank=True,
                                  help_text="Short code for URL shortening")
    
    # QR Code customization
    qr_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='png')
    size = models.IntegerField(default=10, help_text="Scale factor for QR code size")
    error_correction = models.CharField(max_length=1, choices=ERROR_CORRECTION_CHOICES, 
                                       default='M')
    border = models.IntegerField(default=4, help_text="Border size (quiet zone)")
    
    # Colors
    background_color = models.CharField(max_length=20, default='white', 
                                       help_text="Background color (hex, name, or 'transparent')")
    foreground_color = models.CharField(max_length=20, default='black',
                                       help_text="Foreground (data) color")
    
    # File storage
    image_file = models.CharField(max_length=255, help_text="Path to generated image file")
    
    # Analytics
    scan_count = models.IntegerField(default=0, help_text="Number of times QR code was scanned")
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['short_code']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        return f"QRCode {self.id} - {self.content[:50]}"
    
    def save(self, *args, **kwargs):
        # Generate short code if URL shortening is enabled and code doesn't exist
        if self.use_url_shortening and not self.short_code:
            self.short_code = generate_short_code()
            # Ensure uniqueness
            while QRCode.objects.filter(short_code=self.short_code).exists():
                self.short_code = generate_short_code()
        
        super().save(*args, **kwargs)
    
    def get_redirect_url(self):
        """Get the full redirect URL for this QR code."""
        from django.conf import settings
        if self.short_code:
            return f"{settings.QR_CODE_BASE_URL}{settings.QR_CODE_REDIRECT_PATH}{self.short_code}"
        return None
    
    def increment_scan_count(self):
        """Increment the scan count and update last scanned timestamp."""
        from django.utils import timezone
        self.scan_count += 1
        self.last_scanned_at = timezone.now()
        self.save(update_fields=['scan_count', 'last_scanned_at'])
