from django.db import models
from django.conf import settings


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Ativa'),
        ('trialing', 'Período de teste'),
        ('past_due', 'Pagamento em atraso'),
        ('canceled', 'Cancelada'),
        ('unpaid', 'Não paga'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    stripe_subscription_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    plan_name = models.CharField(max_length=255)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.plan_name} ({self.status})"
