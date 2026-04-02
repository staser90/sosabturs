from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'stripe_customer_id', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('Stripe', {'fields': ('stripe_customer_id',)}),
    )
