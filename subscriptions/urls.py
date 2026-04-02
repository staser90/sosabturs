from django.urls import path
from . import views

urlpatterns = [
    path('current/', views.current_subscription, name='current_subscription'),
    path('cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('reactivate/', views.reactivate_subscription, name='reactivate_subscription'),
    path('portal/', views.create_portal_session, name='create_portal_session'),
]
