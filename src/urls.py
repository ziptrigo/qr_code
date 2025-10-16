from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QRCodeViewSet, redirect_view

router = DefaultRouter()
router.register(r'qrcodes', QRCodeViewSet, basename='qrcode')

urlpatterns = [
    path('api/', include(router.urls)),
    path('go/<str:short_code>/', redirect_view, name='qrcode-redirect'),
]
