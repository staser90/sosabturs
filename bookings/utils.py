from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import Booking


def send_booking_confirmation_email(booking):
    """Enviar email de confirmação de reserva"""
    try:
        subject = f'Confirmação de Reserva - {booking.pack_name}'
        
        context = {
            'booking': booking,
            'user': booking.user,
            'site_url': settings.FRONTEND_URL,
        }
        
        # Renderizar template HTML
        html_message = render_to_string('emails/booking_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        # Enviar email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f'Erro ao enviar email de confirmação: {e}')
        return False


def send_booking_update_email(booking, headline=None, changed_fields=None):
    """Enviar email ao cliente quando a reserva é atualizada no admin."""
    try:
        subject = f'Atualização da sua reserva #{booking.id} - SO SAB'

        context = {
            'booking': booking,
            'user': booking.user,
            'site_url': settings.FRONTEND_URL,
            'headline': headline or 'A sua reserva foi atualizada',
            'changed_fields': changed_fields or [],
        }

        html_message = render_to_string('emails/booking_update.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=True,
        )
        return True
    except Exception as e:
        print(f'Erro ao enviar email de atualização: {e}')
        return False


def send_booking_receipt_email(booking):
    """Enviar email com recibo da compra"""
    try:
        subject = f'Recibo de Pagamento - Reserva #{booking.id}'
        
        context = {
            'booking': booking,
            'user': booking.user,
            'site_url': settings.FRONTEND_URL,
        }
        
        # Renderizar template HTML
        html_message = render_to_string('emails/booking_receipt.html', context)
        plain_message = strip_tags(html_message)
        
        # Enviar email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f'Erro ao enviar email de recibo: {e}')
        return False


def send_booking_reminder_email(booking):
    """Enviar lembrete antes do tour (se tiver data marcada)"""
    if not booking.booking_date:
        return False
        
    try:
        subject = f'Lembrete: Seu tour está chegando! - {booking.pack_name}'
        
        context = {
            'booking': booking,
            'user': booking.user,
            'site_url': settings.FRONTEND_URL,
        }
        
        # Renderizar template HTML
        html_message = render_to_string('emails/booking_reminder.html', context)
        plain_message = strip_tags(html_message)
        
        # Enviar email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f'Erro ao enviar email de lembrete: {e}')
        return False
