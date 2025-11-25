from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    QRCodeViewSet,
    dashboard,
    hello_api,
    hello_page,
    home_page,
    login_page,
    login_view,
    logout_page,
    redirect_view,
    register_page,
    signup,
)

router = DefaultRouter()
router.register(r'qrcodes', QRCodeViewSet, basename='qrcode')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/hello', hello_api, name='hello-api'),
    path('api/signup', signup, name='signup'),
    path('api/login', login_view, name='login'),
    path('', home_page, name='home'),
    path('login/', login_page, name='login-page'),
    path('logout/', logout_page, name='logout-page'),
    path('register/', register_page, name='register-page'),
    path('dashboard/', dashboard, name='dashboard'),
    path('hello/', hello_page, name='hello-page'),
    path('go/<str:short_code>/', redirect_view, name='qrcode-redirect'),
]
