"""Async authentication endpoints for Django Ninja."""

from asgiref.sync import sync_to_async
from django.contrib.auth import authenticate, get_user_model
from ninja import Router
from ninja_jwt.authentication import AsyncJWTAuth

from src.qr_code.schemas import (
    LoginSchema,
    SignupSchema,
    TokenResponseSchema,
    UserResponseSchema,
)

User = get_user_model()
router = Router()


@router.post('/signup', response={201: dict}, auth=None)
async def signup(request, payload: SignupSchema):
    """Create a new user account and send confirmation email."""
    # Check if user exists
    exists = await sync_to_async(User.objects.filter(email=payload.email).exists)()
    if exists:
        return 400, {'detail': 'User with that email already exists.'}

    # Create user
    await sync_to_async(User.objects.create_user)(
        username=payload.email,
        email=payload.email,
        password=payload.password,
        name=payload.name,
    )

    # TODO: Send confirmation email using JWT token

    return 201, {'message': 'Account created! Please check your email to confirm your address.'}


@router.post('/login', response=TokenResponseSchema, auth=None)
async def login_view(request, payload: LoginSchema):
    """Authenticate user and return JWT tokens."""
    user = await sync_to_async(authenticate)(
        request, username=payload.email, password=payload.password
    )

    if user is None:
        return 400, {'detail': 'Invalid credentials.'}

    if not user.email_confirmed:
        return 403, {
            'detail': 'Please confirm your email address before logging in. '
            'Check your inbox for the confirmation link.'
        }

    # Generate JWT tokens using ninja-jwt
    from ninja_jwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)

    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@router.get('/me', response=UserResponseSchema, auth=AsyncJWTAuth())
async def get_current_user(request):
    """Get current authenticated user info."""
    return await sync_to_async(lambda: request.auth)()


# Additional endpoints to implement:
# - POST /confirm-email (async)
# - POST /resend-confirmation (async)
# - POST /forgot-password (async)
# - POST /reset-password (async)
# - PUT /account (async) - with AsyncJWTAuth
# - POST /change-password (async) - with AsyncJWTAuth
