from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..models import QRCode
from ..serializers import QRCodeCreateSerializer, QRCodeSerializer


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
