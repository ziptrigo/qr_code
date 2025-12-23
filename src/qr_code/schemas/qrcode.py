"""Pydantic schemas for QR code endpoints."""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator
from ninja import ModelSchema, Schema
from pydantic import field_validator

from src.qr_code.models import QRCode, QRCodeType


class QRCodeCreateSchema(ModelSchema):
    """Schema for creating QR codes."""

    url: str | None = None
    data: str | None = None

    class Meta:
        model = QRCode
        fields = [
            'name',
            'qr_type',
            'qr_format',
            'size',
            'error_correction',
            'border',
            'background_color',
            'foreground_color',
            'use_url_shortening',
        ]

    @field_validator('qr_type')
    @classmethod
    def validate_qr_type_and_content(cls, v: str, info) -> str:
        """Validate qr_type and ensure appropriate content is provided."""
        # Get url and data from the model data
        data = info.data
        url = data.get('url')
        data_field = data.get('data')

        # Ensure either url or data is provided
        if not url and not data_field:
            raise ValueError("Either 'url' or 'data' must be provided")
        if url and data_field:
            raise ValueError("Provide either 'url' or 'data', not both")

        # Validate URL format when qr_type is 'url'
        if v == QRCodeType.URL:
            content = url or data_field
            url_validator = URLValidator()
            try:
                url_validator(content)
            except DjangoValidationError:
                raise ValueError('Please provide a valid URL when type is URL')

        return v


class QRCodeUpdateSchema(ModelSchema):
    """Schema for updating QR codes (name only)."""

    class Meta:
        model = QRCode
        fields = ['name']


class QRCodeSchema(ModelSchema):
    """Schema for QR code response."""

    image_url: str | None = None
    redirect_url: str | None = None

    class Meta:
        model = QRCode
        fields = [
            'id',
            'name',
            'qr_type',
            'content',
            'original_url',
            'use_url_shortening',
            'short_code',
            'qr_format',
            'size',
            'error_correction',
            'border',
            'background_color',
            'foreground_color',
            'image_file',
            'scan_count',
            'last_scanned_at',
            'created_at',
            'updated_at',
        ]


class QRCodePreviewSchema(Schema):
    """Schema for QR code preview response."""

    image_url: str
