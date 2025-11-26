from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import (
    QRCodeViewSet,
    hello_api,
    login_view,
    qrcode_preview,
    redirect_view,
    signup,
)
from .views import (
    dashboard,
    hello_page,
    home_page,
    login_page,
    logout_page,
    qrcode_generator,
    register_page,
)

router = DefaultRouter()
router.register(r'qrcodes', QRCodeViewSet, basename='qrcode')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/hello', hello_api, name='hello-api'),
    path('api/signup', signup, name='signup'),
    path('api/login', login_view, name='login'),
    path('api/qrcodes/preview', qrcode_preview, name='qrcode-preview'),
    path('', home_page, name='home'),
    path('login/', login_page, name='login-page'),
    path('logout/', logout_page, name='logout-page'),
    path('register/', register_page, name='register-page'),
    path('dashboard/', dashboard, name='dashboard'),
    path('qrcodes/new/', qrcode_generator, name='qrcode-new'),
    path('hello/', hello_page, name='hello-page'),
    path('go/<str:short_code>/', redirect_view, name='qrcode-redirect'),
]
