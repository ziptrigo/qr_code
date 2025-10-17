from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import QRCode
from .serializers import QRCodeCreateSerializer, QRCodeSerializer


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
