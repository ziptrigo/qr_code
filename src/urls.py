from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QRCodeViewSet, hello_api, hello_page, redirect_view

router = DefaultRouter()
router.register(r'qrcodes', QRCodeViewSet, basename='qrcode')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/hello', hello_api, name='hello-api'),
    path('hello/', hello_page, name='hello-page'),
    path('go/<str:short_code>/', redirect_view, name='qrcode-redirect'),
]
