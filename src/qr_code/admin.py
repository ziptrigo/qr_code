from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import QRCode, User
from .models.time_limited_token import TimeLimitedToken


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin interface for User."""

    # Extend the default fieldsets with our custom fields.
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            'Custom Fields',
            {
                'fields': (
                    'name',
                    'email_confirmed',
                    'email_confirmed_at',
                )
            },
        ),
    )  # type: ignore[assignment,operator]

    # Add email confirmation status to list display
    list_display = ['username', 'email', 'name', 'email_confirmed', 'is_staff', 'is_active']
    list_filter = ['email_confirmed', 'is_staff', 'is_active', 'is_superuser']
    readonly_fields = ['email_confirmed_at']


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_preview', 'qr_format', 'created_by', 'scan_count', 'created_at']
    list_filter = ['qr_format', 'use_url_shortening', 'created_at']
    search_fields = ['content', 'original_url', 'short_code']
    readonly_fields = ['id', 'created_at', 'updated_at', 'scan_count', 'last_scanned_at']

    @admin.display(description='Content')
    def content_preview(self, obj: QRCode) -> str:
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content


@admin.register(TimeLimitedToken)
class TimeLimitedTokenAdmin(admin.ModelAdmin):
    """Admin interface for TimeLimitedToken."""

    list_display = ['id', 'user', 'token_type', 'created_at', 'used_at', 'is_expired', 'is_used']
    list_filter = ['token_type', 'created_at', 'used_at']
    search_fields = ['user__email', 'user__username', 'token']
    readonly_fields = ['id', 'token', 'created_at', 'used_at', 'is_expired', 'is_used']
    
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'id',
                    'user',
                    'token',
                    'token_type',
                )
            },
        ),
        (
            'Status',
            {
                'fields': (
                    'created_at',
                    'used_at',
                    'is_expired',
                    'is_used',
                )
            },
        ),
    )
    
    @admin.display(description='Expired', boolean=True)
    def is_expired(self, obj: TimeLimitedToken) -> bool:
        return obj.is_expired
    
    @admin.display(description='Used', boolean=True)
    def is_used(self, obj: TimeLimitedToken) -> bool:
        return obj.is_used
