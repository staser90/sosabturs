from django.urls import path
from . import panel_views

urlpatterns = [
    path('bookings/', panel_views.PanelBookingListCreate.as_view(), name='panel-booking-list'),
    path('bookings/<int:pk>/', panel_views.PanelBookingDetail.as_view(), name='panel-booking-detail'),
    path('reviews/', panel_views.PanelReviewListCreate.as_view(), name='panel-review-list'),
    path('reviews/<int:pk>/', panel_views.PanelReviewDetail.as_view(), name='panel-review-detail'),
    path('messages/', panel_views.PanelContactMessageListCreate.as_view(), name='panel-message-list'),
    path('messages/<int:pk>/', panel_views.PanelContactMessageDetail.as_view(), name='panel-message-detail'),
    path('users/', panel_views.PanelUserList.as_view(), name='panel-user-list'),
]
