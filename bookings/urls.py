from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('', views.BookingListCreateView.as_view(), name='booking_list'),
    path('<int:pk>/', csrf_exempt(views.BookingDetailView.as_view()), name='booking_detail'),
    path('<int:pk>/receipt/', views.booking_receipt_html, name='booking-receipt'),
    path('<int:pk>/delete/', csrf_exempt(views.booking_delete), name='booking-delete'),
    path('<int:pk>/cancel/', views.booking_cancel, name='booking-cancel'),
    path('reviews/', views.ReviewListCreateView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
    path('gallery-images/', views.gallery_images, name='gallery-images'),
]
