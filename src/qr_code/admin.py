from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import QRCode, User


@admin.register(User)
class UserAdmin(UserAdmin):
    """Admin interface for User."""

    fieldsets = UserAdmin.fieldsets + (('Custom Fields', {'fields': ('name',)}),)


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_preview', 'qr_format', 'created_by', 'scan_count', 'created_at']
    list_filter = ['qr_format', 'use_url_shortening', 'created_at']
    search_fields = ['content', 'original_url', 'short_code']
    readonly_fields = ['id', 'created_at', 'updated_at', 'scan_count', 'last_scanned_at']

    @admin.display(description='Content')
    def content_preview(self, obj: QRCode) -> str:
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
