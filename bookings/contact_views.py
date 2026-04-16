"""View da página de contacto e processamento do formulário."""
import logging

from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import ContactMessage

logger = logging.getLogger(__name__)


def contact_page(request):
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        subject = (request.POST.get('subject') or '').strip()
        message = (request.POST.get('message') or '').strip()

        errors = []
        if not name:
            errors.append('O nome é obrigatório.')
        if not email:
            errors.append('O email é obrigatório.')
        elif '@' not in email:
            errors.append('Indique um email válido.')
        if not message:
            errors.append('A mensagem é obrigatória.')

        if errors:
            return render(request, 'contacto.html', {
                'errors': errors,
                'form_data': {'name': name, 'email': email, 'subject': subject, 'message': message},
            })

        ContactMessage.objects.create(name=name, email=email, subject=subject or 'Contacto do site', message=message)

        admin_email = getattr(settings, 'BOOKING_NOTIFICATION_EMAIL', '') or ''
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        if admin_email and from_email:
            try:
                subj = f'[Contacto site] {subject or "Sem assunto"}'
                ctx = {
                    'name': name,
                    'email': email,
                    'subject': subject or 'Contacto do site',
                    'message': message,
                    'site_url': getattr(settings, 'FRONTEND_URL', '') or '',
                }
                html = render_to_string('emails/contact_admin.html', ctx)
                send_mail(
                    subject=subj,
                    message=strip_tags(html),
                    from_email=from_email,
                    recipient_list=[admin_email],
                    html_message=html,
                    fail_silently=True,
                )
            except Exception as exc:
                logger.warning('Falha ao enviar email de contacto: %s', exc)

        messages.success(request, 'Mensagem enviada com sucesso. Responderemos em breve.')
        return redirect('contacto')

    return render(request, 'contacto.html')
