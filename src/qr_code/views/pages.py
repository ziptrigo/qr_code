from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from ..models import QRCode


def hello_page(request: HttpRequest) -> HttpResponse:
    """Render the hello page (GET /hello/)."""
    return render(request, 'hello.html')


def home_page(request: HttpRequest) -> HttpResponse:
    """Render the homepage (GET /)."""
    return render(request, 'home.html')


def login_page(request: HttpRequest) -> HttpResponse:
    """Render the login page (GET /login/)."""
    return render(request, 'login.html')


def register_page(request: HttpRequest) -> HttpResponse:
    """Render the register page (GET /register/)."""
    return render(request, 'register.html')


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

    qrcodes = QRCode.objects.filter(created_by=user)

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
def qrcode_generator(request: HttpRequest) -> HttpResponse:
    """Render the QR code generator page."""
    return render(request, 'qrcode_generator.html')
