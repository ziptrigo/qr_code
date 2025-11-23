from django.contrib.auth import authenticate, get_user_model, login
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .auth_serializers import LoginSerializer, SignupSerializer
from .models import QRCode
from .serializers import QRCodeCreateSerializer, QRCodeSerializer

User = get_user_model()


class QRCodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for QR Code operations.

    Endpoints:
    - POST /api/qrcodes/ - Create a new QR code
    - GET /api/qrcodes/ - List all QR codes for authenticated user
    - GET /api/qrcodes/{id}/ - Retrieve a specific QR code
    - DELETE /api/qrcodes/{id}/ - Delete a QR code
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter QR codes by the authenticated user."""
        user = self.request.user
        if user.is_authenticated:
            return QRCode.objects.filter(created_by=user)
        return QRCode.objects.none()

    def get_serializer_class(self):
        """Use different serializers for create vs retrieve."""
        if self.action == 'create':
            return QRCodeCreateSerializer
        return QRCodeSerializer

    def perform_create(self, serializer):
        """Save with the current user."""
        serializer.save()


@api_view(['GET'])
@permission_classes([AllowAny])
def redirect_view(request, short_code):
    """
    Redirect endpoint for shortened URLs.

    This endpoint:
    1. Looks up the QR code by short_code
    2. Increments the scan count
    3. Redirects to the original URL

    Path: /go/{short_code}/
    """
    try:
        qr_code = QRCode.objects.get(short_code=short_code)
    except QRCode.DoesNotExist:
        raise Http404("QR Code not found")

    # Increment scan count
    qr_code.increment_scan_count()

    # Redirect to original URL
    if qr_code.original_url:
        return redirect(qr_code.original_url)
    else:
        return Response(
            {"error": "No redirect URL available for this QR code"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def hello_api(request):
    """
    Simple hello API endpoint.
    Returns a JSON response with a hello message.
    
    Path: /api/hello
    """
    return JsonResponse({'message': 'Hello, world!'})


def hello_page(request):
    """
    Render the hello page.
    
    Path: /hello/
    """
    return render(request, 'hello.html')


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """Signup endpoint: create user, start session, return session id and user info."""
    serializer = SignupSerializer(data=request.data)
    if not serializer.is_valid():
        errors = serializer.errors
        # Special-case email uniqueness per spec
        if 'email' in errors:
            for err in errors['email']:
                if 'User with that email already exists.' in str(err):
                    return Response({'message': 'User with that email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    login(request, user)
    if not request.session.session_key:
        request.session.save()

    return Response(
        {
            'user': {'id': user.id, 'email': user.email, 'name': getattr(user, 'name', '')},
            'sessionid': request.session.session_key,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login endpoint: authenticate by email/password, start session, return session id and user info."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    user = authenticate(request, username=email, password=password)
    if user is None:
        return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

    login(request, user)
    if not request.session.session_key:
        request.session.save()

    return Response(
        {
            'user': {'id': user.id, 'email': user.email, 'name': getattr(user, 'name', '')},
            'sessionid': request.session.session_key,
        }
    )
