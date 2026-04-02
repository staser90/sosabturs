from rest_framework import serializers
from .models import Booking, Review
from accounts.serializers import UserSerializer


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'pack_name', 'pack_price', 'booking_date', 'addons', 'status', 'stripe_payment_intent_id', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    can_review = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_email', 'booking', 'pack_name', 'rating', 'comment', 'created_at', 'updated_at', 'is_approved', 'can_review']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_can_review(self, obj):
        """Verificar se o utilizador atual pode avaliar este pack"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        # Verificar se já tem uma reserva confirmada/completa deste pack
        from .models import Booking
        has_booking = Booking.objects.filter(
            user=request.user,
            pack_name=obj.pack_name,
            status__in=['confirmed', 'completed']
        ).exists()
        
        return has_booking
