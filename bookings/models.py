from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Concluída'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    pack_name = models.CharField(max_length=255)
    pack_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateField(null=True, blank=True)
    addons = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.pack_name} ({self.status})"


class Review(models.Model):
    """Avaliação de um tour/pack por um cliente"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='review', null=True, blank=True)
    pack_name = models.CharField(max_length=255)  # Nome do pack avaliado
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Avaliação de 1 a 5 estrelas"
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False, help_text="Avaliação aprovada pelo admin")

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = [['user', 'pack_name']]  # Um utilizador só pode avaliar cada pack uma vez

    def __str__(self):
        return f"{self.user.email} - {self.pack_name} ({self.rating}⭐)"


class ContactMessage(models.Model):
    """Mensagens enviadas pelo formulário de contacto."""
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contact_messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.subject or '(sem assunto)'}"
