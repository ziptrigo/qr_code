from pathlib import Path
from typing import TYPE_CHECKING

import segno
from django.conf import settings

if TYPE_CHECKING:
    from src.qr_code.models import QRCode


class QRCodeGenerator:
    """Service class for generating QR codes using segno."""

    @staticmethod
    def generate_qr_code(qr_code_instance: QRCode) -> str:
        """Generate a QR code image file based on the QRCode model instance."""
        # Create QR code with segno
        error_level_map = {'L': 'L', 'M': 'M', 'Q': 'Q', 'H': 'H'}

        qr = segno.make(
            qr_code_instance.content,
            error=error_level_map.get(qr_code_instance.error_correction, 'M'),
            micro=False,
        )

        # Prepare file path
        media_qrcodes = Path(settings.MEDIA_ROOT) / 'qrcodes'
        media_qrcodes.mkdir(parents=True, exist_ok=True)

        file_name = f'{qr_code_instance.id}.{qr_code_instance.qr_format}'
        file_path = media_qrcodes / file_name

        # Prepare color values
        bg_color = QRCodeGenerator._parse_color(qr_code_instance.background_color)
        fg_color = QRCodeGenerator._parse_color(qr_code_instance.foreground_color)

        # Generate based on format
        if qr_code_instance.qr_format == 'svg':
            qr.save(
                str(file_path),
                kind='svg',
                scale=qr_code_instance.size,
                border=qr_code_instance.border,
                dark=fg_color,
                light=bg_color,
            )
        else:  # png, pdf, or other formats
            qr.save(
                str(file_path),
                kind=qr_code_instance.qr_format,
                scale=qr_code_instance.size,
                border=qr_code_instance.border,
                dark=fg_color,
                light=bg_color,
            )

        # Return relative path for storage
        return f'qrcodes/{file_name}'

    @staticmethod
    def _parse_color(color_value: str) -> str | None:
        """Parse color value to format accepted by segno."""
        if color_value.lower() == 'transparent':
            return None
        return color_value

    @staticmethod
    def get_file_url(image_file: str) -> str:
        """Get the full URL for accessing the QR code image."""
        return f'{settings.MEDIA_URL}{image_file}'
