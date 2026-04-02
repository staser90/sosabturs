from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views
from . import chatbot_views

urlpatterns = [
    path('register/', csrf_exempt(views.register), name='register'),
    path('login/', csrf_exempt(views.login), name='login'),
    path('logout/', views.logout, name='logout'),
    path('me/', views.me, name='me'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('logout-page/', views.logout_page, name='logout_page'),
    path('chatbot/', chatbot_views.chatbot_message, name='chatbot'),
]
