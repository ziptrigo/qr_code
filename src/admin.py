from django.contrib import admin

from .models import QRCode


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_preview', 'qr_format', 'created_by', 'scan_count', 'created_at']
    list_filter = ['qr_format', 'use_url_shortening', 'created_at']
    search_fields = ['content', 'original_url', 'short_code']
    readonly_fields = ['id', 'created_at', 'updated_at', 'scan_count', 'last_scanned_at']

    @admin.display(description='Content')
    def content_preview(self, obj: QRCode) -> str:
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
