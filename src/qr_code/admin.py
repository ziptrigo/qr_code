import os
from typing import List, Tuple

from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import path
from django.utils import timezone

from .models import QRCode, User
from .models.time_limited_token import TimeLimitedToken
from .services.email_service import get_email_backend


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin interface for User."""

    # Extend the default fieldsets with our custom fields.
    fieldsets = DjangoUserAdmin.fieldsets + (  # type: ignore
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
    list_display = [
        'id',
        'name',
        'content_preview',
        'qr_format',
        'created_by',
        'scan_count',
        'created_at',
        'deleted_at',
    ]
    list_filter = ['qr_format', 'use_url_shortening', 'created_at', 'deleted_at']
    search_fields = ['content', 'original_url', 'short_code']
    readonly_fields = ['id', 'created_at', 'updated_at', 'scan_count', 'last_scanned_at', 'deleted_at']

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


class TestEmailForm(forms.Form):
    recipient: forms.EmailField = forms.EmailField(
        label='Recipient email',
        required=True,
        help_text='Email address to send the test email to.',
        widget=forms.EmailInput(attrs={'size': '60'}),
    )


class CustomAdminSite(admin.AdminSite):
    """Custom admin site with additional tools."""

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('tools/', self.admin_view(self.tools_view), name='admin_tools'),
        ]
        return custom_urls + urls

    def tools_view(self, request: HttpRequest) -> HttpResponse:
        """Custom admin page for various tools."""
        environment_variables = None

        # Restrict access strictly to superusers
        if not request.user.is_superuser:
            messages.error(request, 'You do not have permission to access this page.')
            initial_email = getattr(request.user, 'email', '') or ''
            form = TestEmailForm(initial={'recipient': initial_email})
            context = {
                **self.each_context(request),
                'title': 'Admin Tools',
                'form': form,
                'environment_variables': None,
            }
            return render(request, 'admin/tools.html', context, status=403)

        if request.method == 'POST' and 'send_test_email' in request.POST:
            form = TestEmailForm(request.POST)
            if form.is_valid():
                recipient = form.cleaned_data['recipient']
                current_datetime = timezone.now().strftime('%Y-%m-%d %H:%M:%S %Z')

                subject = 'Test email from the admin panel'
                text_body = (
                    'This is a test email.\n'
                    'Sent from the Django admin panel.\n'
                    f'\nSent: {current_datetime}'
                )

                try:
                    email_backend = get_email_backend()
                    email_backend.send_email(
                        to=recipient,
                        subject=subject,
                        text_body=text_body,
                    )
                    messages.success(request, f'Test email sent to {recipient}')
                    form = TestEmailForm(initial={'recipient': recipient})
                except Exception as e:
                    messages.error(request, f'Failed to send email: {str(e)}')
            else:
                messages.error(request, 'Please correct the errors below.')
        elif request.method == 'POST' and 'show_environment' in request.POST:
            # Show all environment variables
            try:
                # Convert to a sorted list of (key, value) for deterministic display
                raw_env: List[Tuple[str, str]] = sorted(
                    os.environ.items(), key=lambda it: it[0].lower()
                )

                # Exclude specific keys entirely
                EXCLUDED_KEYS = {
                    'DJANGO_SECRET_KEY',
                }

                def is_sensitive(key: str) -> bool:
                    k = key.upper()
                    if any(s in k for s in ['SECRET', 'PASSWORD', 'TOKEN']):
                        return True
                    # Avoid over-masking: 'KEY' alone can be too broad; include if endswith _KEY
                    if k.endswith('_KEY'):
                        return True
                    if k.startswith(('AWS_', 'GCP_', 'AZURE_')):
                        return True
                    return False

                def mask(value: str) -> str:
                    s = str(value)
                    if len(s) <= 4:
                        return '*' * len(s)
                    return '*' * (len(s) - 4) + s[-4:]

                # Build final list with masking
                environment_variables = []
                for key, value in raw_env:
                    if key in EXCLUDED_KEYS:
                        continue
                    display_value = mask(value) if is_sensitive(key) else value
                    environment_variables.append((key, display_value))
                messages.success(request, 'Environment variables loaded.')
            except Exception as e:
                messages.error(request, f'Failed to load environment variables: {str(e)}')
            # Keep the email form initialized for rendering alongside
            initial_email = getattr(request.user, 'email', '') or ''
            form = TestEmailForm(initial={'recipient': initial_email})
        else:
            # Prefill with the logged-in user's email for convenience
            initial_email = getattr(request.user, 'email', '') or ''
            form = TestEmailForm(initial={'recipient': initial_email})

        context = {
            **self.each_context(request),
            'title': 'Admin Tools',
            'form': form,
            'environment_variables': environment_variables,
        }
        return render(request, 'admin/tools.html', context)


# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register models with custom admin site
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(QRCode, QRCodeAdmin)
custom_admin_site.register(TimeLimitedToken, TimeLimitedTokenAdmin)
