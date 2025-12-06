from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import (
    QRCodeViewSet,
    confirm_email,
    forgot_password,
    login_view,
    qrcode_preview,
    redirect_view,
    resend_confirmation,
    reset_password,
    signup,
)
from .views import (
    confirm_email_page,
    dashboard,
    email_confirmation_success,
    forgot_password_page,
    home_page,
    login_page,
    logout_page,
    qrcode_generator,
    register_page,
    reset_password_page,
)

router = DefaultRouter()
router.register(r'qrcodes', QRCodeViewSet, basename='qrcode')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/signup', signup, name='signup'),
    path('api/login', login_view, name='login'),
    path('api/forgot-password', forgot_password, name='forgot-password'),
    path('api/reset-password', reset_password, name='reset-password'),
    path('api/resend-confirmation', resend_confirmation, name='resend-confirmation'),
    path('api/confirm-email', confirm_email, name='confirm-email'),
    path('api/qrcodes/preview', qrcode_preview, name='qrcode-preview'),
    path('', home_page, name='home'),
    path('login/', login_page, name='login-page'),
    path('forgot-password/', forgot_password_page, name='forgot-password-page'),
    path('reset-password/<str:token>/', reset_password_page, name='reset-password-page'),
    path('confirm-email/<str:token>/', confirm_email_page, name='confirm-email-page'),
    path('confirm-email/success/', email_confirmation_success, name='email-confirmation-success'),
    path('logout/', logout_page, name='logout-page'),
    path('register/', register_page, name='register-page'),
    path('dashboard/', dashboard, name='dashboard'),
    path('qrcodes/new/', qrcode_generator, name='qrcode-new'),
    path('go/<str:short_code>/', redirect_view, name='qrcode-redirect'),
]
