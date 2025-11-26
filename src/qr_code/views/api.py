from django.contrib.auth import authenticate, get_user_model, login
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..auth_serializers import LoginSerializer, SignupSerializer
from ..models import QRCode
from ..serializers import QRCodeCreateSerializer, QRCodeSerializer

User = get_user_model()


class QRCodeViewSet(viewsets.ModelViewSet):
    """ViewSet for QR Code operations."""

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
    """Redirect endpoint for shortened URLs."""
    try:
        qr_code = QRCode.objects.get(short_code=short_code)
    except QRCode.DoesNotExist:
        msg = 'QR Code not found'
        raise Http404(msg)

    qr_code.increment_scan_count()

    if qr_code.original_url:
        return redirect(qr_code.original_url)

    return Response(
        {"error": "No redirect URL available for this QR code"},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def hello_api(request):
    """Simple hello API endpoint."""
    return JsonResponse({'message': 'Hello, world!'})


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """Signup endpoint: create user, start session, return session id and user info."""
    serializer = SignupSerializer(data=request.data)
    if not serializer.is_valid():
        errors = serializer.errors
        if 'email' in errors:
            for err in errors['email']:
                if 'User with that email already exists.' in str(err):
                    return Response(
                        {'message': 'User with that email already exists.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
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
    """Login endpoint: authenticate and start session with optional remember flag."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    user = authenticate(request, username=email, password=password)
    if user is None:
        return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

    login(request, user)

    remember_raw = str(request.data.get('remember', '')).lower()
    remember = remember_raw in {'1', 'true', 'on', 'yes'}
    request.session.set_expiry(1209600 if remember else 0)

    if not request.session.session_key:
        request.session.save()

    return Response(
        {
            'user': {'id': user.id, 'email': user.email, 'name': getattr(user, 'name', '')},
            'sessionid': request.session.session_key,
        }
    )
