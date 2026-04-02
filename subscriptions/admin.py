from django.contrib import admin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_name', 'status', 'current_period_end', 'cancel_at_period_end', 'created_at')
    list_filter = ('status', 'cancel_at_period_end')
    search_fields = ('user__email', 'user__username', 'stripe_subscription_id')
    readonly_fields = ('created_at', 'updated_at')
