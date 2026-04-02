"""API do painel de gestão: CRUD para Booking, Review, ContactMessage. Apenas staff."""
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Booking, Review, ContactMessage
from .panel_serializers import (
    PanelBookingSerializer,
    PanelReviewSerializer,
    PanelContactMessageSerializer,
)
from accounts.models import User
from accounts.serializers import UserSerializer


# --- Reservas (Booking) ---
class PanelBookingListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PanelBookingSerializer
    queryset = Booking.objects.all().select_related('user').order_by('-created_at')
    pagination_class = None


class PanelBookingDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PanelBookingSerializer
    queryset = Booking.objects.all().select_related('user')


# --- Avaliações (Review) ---
class PanelReviewListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PanelReviewSerializer
    queryset = Review.objects.all().select_related('user').order_by('-created_at')
    pagination_class = None


class PanelReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PanelReviewSerializer
    queryset = Review.objects.all().select_related('user')


# --- Mensagens de contacto ---
class PanelContactMessageListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PanelContactMessageSerializer
    queryset = ContactMessage.objects.all().order_by('-created_at')
    pagination_class = None


class PanelContactMessageDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PanelContactMessageSerializer
    queryset = ContactMessage.objects.all()


# --- Utilizadores (só leitura para dropdowns) ---
class PanelUserList(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-date_joined')
    pagination_class = None


# --- Página do painel (HTML) ---
@staff_member_required(login_url='/login.html')
def panel_page(request):
    """Renderiza a página do painel. Apenas utilizadores staff."""
    return render(request, 'panel.html')
