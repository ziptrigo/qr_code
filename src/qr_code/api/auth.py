from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model, login
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..auth_serializers import LoginSerializer, SignupSerializer
from ..services.password_reset import PasswordResetService, get_password_reset_service

User = get_user_model()


def _get_password_reset_service() -> PasswordResetService:
    return get_password_reset_service()


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


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Start password reset flow for the given email.

    The response is always 200 with a generic message, regardless of whether the
    email exists.
    """

    email = str(request.data.get('email', '')).strip()
    if not email:
        return Response(
            {'email': ['This field is required.']},
            status=status.HTTP_400_BAD_REQUEST,
        )

    service = _get_password_reset_service()
    service.request_reset(email=email)

    return Response(
        {
            'detail': (
                'If the account exists, an email will be sent with a password '
                'reset link.'
            ),
        },
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password using a valid token."""

    token = str(request.data.get('token', '')).strip()
    password = str(request.data.get('password', ''))
    password_confirm = str(request.data.get('password_confirm', ''))

    errors: dict[str, list[str]] = {}
    if not token:
        errors.setdefault('token', []).append('This field is required.')
    if not password:
        errors.setdefault('password', []).append('This field is required.')
    if not password_confirm:
        errors.setdefault('password_confirm', []).append('This field is required.')
    if password and password_confirm and password != password_confirm:
        errors.setdefault('password_confirm', []).append('Passwords do not match.')

    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    service = _get_password_reset_service()
    token_obj = service.validate_token(token)
    if token_obj is None:
        return Response(
            {'detail': 'Invalid or expired token.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = token_obj.user
    user.set_password(password)
    user.save(update_fields=['password'])
    service.mark_used(token_obj)

    return Response({'detail': 'Password has been reset.'}, status=status.HTTP_200_OK)
