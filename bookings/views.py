from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
import os
from django.conf import settings
from .models import Booking, Review
from .serializers import BookingSerializer, ReviewSerializer


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookingDetailView(generics.RetrieveDestroyAPIView):
    """Ver (GET) ou eliminar (DELETE) uma reserva do utilizador."""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def booking_delete(request, pk):
    """Eliminar uma reserva do perfil do utilizador (apaga da base de dados)."""
    booking = get_object_or_404(Booking, pk=pk)
    if booking.user_id != request.user.id:
        return Response({'error': 'Não autorizado'}, status=status.HTTP_403_FORBIDDEN)
    booking.delete()
    return Response({'deleted': True, 'id': pk}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def booking_cancel(request, pk):
    """Cancelar uma reserva do utilizador (marca como cancelada)."""
    booking = get_object_or_404(Booking, pk=pk)
    if booking.user_id != request.user.id:
        return Response({'error': 'Não autorizado'}, status=status.HTTP_403_FORBIDDEN)
    if booking.status == 'cancelled':
        return Response({'message': 'Reserva já estava cancelada'}, status=status.HTTP_200_OK)
    booking.status = 'cancelled'
    booking.save(update_fields=['status'])
    return Response({'message': 'Reserva cancelada', 'status': 'cancelled'}, status=status.HTTP_200_OK)


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]  # Permitir ver avaliações sem login

    def get_queryset(self):
        # Mostrar apenas avaliações aprovadas
        queryset = Review.objects.filter(is_approved=True)
        
        # Filtrar por pack_name se fornecido
        pack_name = self.request.query_params.get('pack_name', None)
        if pack_name:
            queryset = queryset.filter(pack_name__icontains=pack_name)
        
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        # Verificar se o utilizador tem uma reserva confirmada deste pack
        pack_name = serializer.validated_data.get('pack_name')
        user = self.request.user
        
        if not user.is_authenticated:
            return Response(
                {'error': 'É necessário estar autenticado para avaliar'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verificar se já existe avaliação deste utilizador para este pack
        existing_review = Review.objects.filter(user=user, pack_name=pack_name).first()
        if existing_review:
            return Response(
                {'error': 'Você já avaliou este pack'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar se tem reserva confirmada/completa
        has_booking = Booking.objects.filter(
            user=user,
            pack_name=pack_name,
            status__in=['confirmed', 'completed']
        ).exists()
        
        if not has_booking:
            return Response(
                {'error': 'Você precisa ter uma reserva confirmada para avaliar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(user=user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_receipt_html(request, pk):
    """Devolve HTML do recibo da reserva para imprimir / guardar como PDF."""
    booking = get_object_or_404(Booking, pk=pk)
    if booking.user_id != request.user.id:
        return Response({'error': 'Não autorizado'}, status=status.HTTP_403_FORBIDDEN)
    site_url = request.build_absolute_uri('/').rstrip('/')
    html = render_to_string('emails/booking_receipt.html', {
        'booking': booking,
        'user': booking.user,
        'site_url': site_url,
        'is_web': True,
    })
    return HttpResponse(html, content_type='text/html')


@api_view(['GET'])
@permission_classes([AllowAny])
def gallery_images(request):
    """Retornar lista de imagens da galeria"""
    gallery_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR / 'static', 'images', 'galeria')
    
    # Se STATIC_ROOT não existir, usar BASE_DIR/static
    if not os.path.exists(gallery_path):
        gallery_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'galeria')
    
    images = []
    if os.path.exists(gallery_path):
        for filename in sorted(os.listdir(gallery_path)):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                # Usar URL estática do Django
                image_url = f'/static/images/galeria/{filename}'
                images.append({
                    'url': image_url,
                    'filename': filename
                })
    
    return JsonResponse({'images': images})
