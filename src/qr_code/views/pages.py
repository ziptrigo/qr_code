from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from ..models import QRCode
from ..services.email_confirmation import get_email_confirmation_service
from ..services.password_reset import PasswordResetService, get_password_reset_service


def home_page(request: HttpRequest) -> HttpResponse:
    """Render the homepage (GET /).

    If the user is authenticated, redirect to the dashboard instead.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def login_page(request: HttpRequest) -> HttpResponse:
    """Render the login page (GET /login/)."""
    return render(request, 'login.html')


def forgot_password_page(request: HttpRequest) -> HttpResponse:
    """Render the forgot password page (GET /forgot-password/)."""
    return render(request, 'forgot_password.html')


def reset_password_page(request: HttpRequest, token: str) -> HttpResponse:
    """Render the reset password page or expired page based on token."""

    service: PasswordResetService = get_password_reset_service()
    token_obj = service.validate_token(token)
    if token_obj is None:
        return render(request, 'reset_password_expired.html')

    return render(request, 'reset_password.html', {'token': token})


def register_page(request: HttpRequest) -> HttpResponse:
    """Render the register page (GET /register/)."""
    return render(request, 'register.html')


def account_created_page(request: HttpRequest) -> HttpResponse:
    """Render the account created confirmation page."""
    return render(request, 'account_created.html')


def logout_page(request: HttpRequest) -> HttpResponse:
    """Log out the current user and redirect to the homepage."""
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Render the user dashboard with their QR codes."""
    user = request.user

    # Narrow type for static checkers; guarded by @login_required.
    if isinstance(user, AnonymousUser):
        raise RuntimeError('Authenticated user required')

    query = request.GET.get('q', '')
    sort = request.GET.get('sort', '')

    qrcodes = QRCode.objects.filter(created_by=user, deleted_at__isnull=True)

    if query:
        qrcodes = qrcodes.filter(name__icontains=query)

    if sort == 'name':
        qrcodes = qrcodes.order_by('name')
    else:
        qrcodes = qrcodes.order_by('-created_at')

    context = {
        'qrcodes': qrcodes,
        'query': query,
    }
    return render(request, 'dashboard.html', context)


@login_required
def qrcode_editor(request: HttpRequest, qr_id: str | None = None) -> HttpResponse:
    """Render the QR code editor page for creating or editing QR codes.

    Args:
        request: The HTTP request object.
        qr_id: Optional UUID of the QR code to edit. If None, create mode.
    """
    user = request.user

    # Narrow type for static checkers; guarded by @login_required.
    if isinstance(user, AnonymousUser):
        raise RuntimeError('Authenticated user required')

    qrcode = None
    if qr_id:
        # Edit mode: fetch the QR code and validate ownership
        try:
            qrcode = QRCode.objects.get(id=qr_id, created_by=user)
        except QRCode.DoesNotExist:
            # Return 404 if QR code doesn't exist or doesn't belong to user
            from django.http import Http404

            msg = 'QR Code not found'
            raise Http404(msg)

    context = {'qrcode': qrcode, 'prefill': {}}
    return render(request, 'qrcode_editor.html', context)


@login_required
def qrcode_duplicate(request: HttpRequest, qr_id: str) -> HttpResponse:
    """Render the QR code editor in create mode, pre-filled from an existing QR code.

    The resulting page behaves like create (POST to create endpoint), but inputs are
    initialized with the values from the referenced QR code. The short URL is not
    copied; if tracking is enabled, a new short code will be generated upon creation.
    """
    user = request.user

    # Narrow type for static checkers; guarded by @login_required.
    if isinstance(user, AnonymousUser):
        raise RuntimeError('Authenticated user required')

    try:
        source = QRCode.objects.get(id=qr_id, created_by=user)
    except QRCode.DoesNotExist:
        from django.http import Http404

        msg = 'QR Code not found'
        raise Http404(msg)

    # Prefer the original URL (if present) for URL-type QR codes; otherwise use content.
    if source.qr_type == 'url' and source.original_url:
        prefill_content = source.original_url
    else:
        prefill_content = source.content

    prefill = {
        'name': source.name,
        'qr_type': source.qr_type,
        'qr_format': source.qr_format,
        'content': prefill_content,
        'use_url_shortening': bool(source.use_url_shortening and source.qr_type == 'url'),
    }

    context = {
        'qrcode': None,
        'prefill': prefill,
    }
    return render(request, 'qrcode_editor.html', context)


def confirm_email_page(request: HttpRequest, token: str) -> HttpResponse:
    """Validate email confirmation token and redirect accordingly."""

    service = get_email_confirmation_service()
    token_obj = service.validate_token(token)

    if token_obj is None:
        return render(request, 'email_confirmation_expired.html')

    # Confirm the email
    service.confirm_email(token_obj)
    return redirect('email-confirmation-success')


def email_confirmation_success(request: HttpRequest) -> HttpResponse:
    """Render the email confirmation success page."""
    return render(request, 'email_confirmation_success.html')
