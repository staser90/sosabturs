"""View da página de contacto e processamento do formulário."""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import ContactMessage


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
        messages.success(request, 'Mensagem enviada com sucesso. Responderemos em breve.')
        return redirect('contacto')

    return render(request, 'contacto.html')
