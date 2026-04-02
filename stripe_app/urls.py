from django.urls import path
from . import views

urlpatterns = [
    path('create-booking-checkout/', views.create_booking_checkout, name='create_booking_checkout'),
    path('confirm-booking/', views.confirm_booking_from_session, name='confirm_booking'),
    path('webhook/', views.webhook, name='stripe_webhook'),
]
