"""Main Django Ninja API router configuration."""

from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

# Create the main API instance
api = NinjaExtraAPI(
    title='QR Code API',
    version='2.0.0',
    description='QR Code generation and management API with JWT authentication',
)

# Register JWT authentication controllers (login, refresh, verify)
api.register_controllers(NinjaJWTDefaultController)

# Import and add routers
# These will be imported after defining them
# from .auth import router as auth_router
# from .qrcode import router as qrcode_router
# from .redirect import router as redirect_router

# api.add_router('/auth/', auth_router, tags=['Authentication'])
# api.add_router('/qrcodes/', qrcode_router, tags=['QR Codes'])
# api.add_router('/go/', redirect_router, tags=['Redirect'])
