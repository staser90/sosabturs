"""Serializers para a API do painel (CRUD completo, staff only)."""
from rest_framework import serializers
from .models import Booking, Review, ContactMessage
from accounts.models import User


class PanelBookingSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'user_email', 'pack_name', 'pack_price', 'booking_date',
            'addons', 'status', 'stripe_payment_intent_id', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class PanelReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_email', 'booking', 'pack_name', 'rating',
            'comment', 'is_approved', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PanelContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserChoiceSerializer(serializers.ModelSerializer):
    """Lista mínima de utilizadores para dropdowns no painel."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
