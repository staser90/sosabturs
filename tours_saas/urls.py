"""
URL configuration for tours_saas project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import password_reset_views as pwd_reset_views

admin.site.site_header = 'SO SAB – Painel de Gestão'
admin.site.site_title = 'SO SAB'
admin.site.index_title = 'Gestão do site'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/auth/', include('accounts.urls')),
    path('api/stripe/', include('stripe_app.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/panel/', include('bookings.panel_urls')),
    path('accounts/', include('allauth.urls')),
    # Recuperação de senha (disponível em dev e produção)
    path('recuperar-senha/', pwd_reset_views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('recuperar-senha/enviado/', pwd_reset_views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('recuperar-senha/<uidb64>/<token>/', pwd_reset_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('recuperar-senha/concluido/', pwd_reset_views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

# Servir arquivos estáticos e media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Servir templates HTML
    from django.views.generic import TemplateView
    from accounts import views as accounts_views
    from accounts import password_reset_views as pwd_reset_views
    from bookings.contact_views import contact_page
    from bookings.panel_views import panel_page
    urlpatterns += [
        path('', TemplateView.as_view(template_name='index.html'), name='home'),
        path('login.html', accounts_views.login_page, name='login'),
        path('register.html', TemplateView.as_view(template_name='register.html'), name='register'),
        path('dashboard.html', accounts_views.dashboard_page, name='dashboard'),
        path('logout.html', accounts_views.logout_page, name='logout_redirect'),
        path('checkout.html', TemplateView.as_view(template_name='checkout.html'), name='checkout'),
        path('success.html', TemplateView.as_view(template_name='success.html'), name='success'),
        path('catalogo.html', TemplateView.as_view(template_name='catalogo.html'), name='catalogo'),
        path('transfers.html', TemplateView.as_view(template_name='transfers.html'), name='transfers'),
        path('galeria.html', TemplateView.as_view(template_name='galeria.html'), name='galeria'),
        path('contacto.html', contact_page, name='contacto'),
        path('profile.html', accounts_views.profile_page, name='profile'),
        path('painel.html', panel_page, name='panel'),
        # Recuperação de senha
        path('recuperar-senha/', pwd_reset_views.CustomPasswordResetView.as_view(), name='password_reset'),
        path('recuperar-senha/enviado/', pwd_reset_views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
        path('recuperar-senha/<uidb64>/<token>/', pwd_reset_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
        path('recuperar-senha/concluido/', pwd_reset_views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    ]
