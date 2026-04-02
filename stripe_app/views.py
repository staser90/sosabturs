from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import importlib
import json
import stripe
from accounts.models import User
from bookings.models import Booking

# Corrigir bug do Stripe onde __getattr__ devolve None para submódulos (apps, billing_portal, etc.),
# causando "'NoneType' object has no attribute 'Secret'". Forçar carregamento dos submódulos.
if getattr(stripe, '__getattr__', None) is not None:
    _orig_stripe_getattr = stripe.__getattr__

    def _stripe_getattr(name):
        if name in ('abstract', 'api_resources'):
            return _orig_stripe_getattr(name)
        try:
            return importlib.import_module('stripe.' + name)
        except ModuleNotFoundError:
            return _orig_stripe_getattr(name)

    stripe.__getattr__ = _stripe_getattr

for _sub in (
    'apps', 'billing_portal', 'checkout', 'climate', 'financial_connections',
    'identity', 'issuing', 'radar', 'reporting', 'sigma', 'tax', 'terminal',
    'test_helpers', 'treasury',
):
    if not hasattr(stripe, _sub) or getattr(stripe, _sub) is None:
        setattr(stripe, _sub, importlib.import_module('stripe.' + _sub))

# Garantir que o Stripe tem sempre uma chave ao carregar
_key = getattr(settings, 'STRIPE_SECRET_KEY', None) or ''
if _key and isinstance(_key, str) and _key.strip():
    stripe.api_key = _key.strip()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking_checkout(request):
    """Criar sessão de checkout para reserva única"""
    # Garantir que a chave do Stripe está configurada
    stripe_secret_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
    
    if not stripe_secret_key:
        return Response(
            {'error': 'Chave do Stripe não configurada. Verifique o arquivo .env e reinicie o servidor Django.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    stripe_secret_key = str(stripe_secret_key).strip()
    
    if not stripe_secret_key or stripe_secret_key == '':
        return Response(
            {'error': 'Chave do Stripe está vazia. Verifique o arquivo .env'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Configurar chave do Stripe antes de usar
    stripe.api_key = stripe_secret_key
    
    # Suportar múltiplos itens do carrinho ou item único (compatibilidade)
    items = request.data.get('items', [])
    pack_name = request.data.get('packName')
    pack_price = request.data.get('packPrice')
    booking_date = request.data.get('bookingDate')
    addons = request.data.get('addons')

    # Se há itens do carrinho, usar esses; senão usar pack único (compatibilidade)
    if items and isinstance(items, list) and len(items) > 0:
        # Processar múltiplos itens do carrinho
        line_items = []
        total_price = 0
        pack_names = []
        
        for item in items:
            item_name = item.get('packName', '')
            item_price = item.get('packPrice', 0)
            
            try:
                item_price = float(item_price)
            except (ValueError, TypeError):
                continue
            
            pack_names.append(item_name)
            total_price += item_price
            
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': item_name,
                        'description': f'Reserva de tour - {item.get("duration", "")}',
                    },
                    'unit_amount': int(item_price * 100),
                },
                'quantity': 1,
            })
        
        if not line_items:
            return Response(
                {'error': 'Nenhum item válido no carrinho'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pack_name = ', '.join(pack_names)
        pack_price = total_price
        
    else:
        # Modo compatibilidade: item único
        if not pack_name:
            return Response(
                {'error': 'packName é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if pack_price is None:
            return Response(
                {'error': 'packPrice é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pack_price = float(pack_price)
        except (ValueError, TypeError):
            return Response(
                {'error': 'packPrice deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        line_items = [{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': pack_name,
                    'description': f'Reserva para {booking_date or "data a definir"}' if booking_date else 'Reserva de tour',
                },
                'unit_amount': int(pack_price * 100),
            },
            'quantity': 1,
        }]

    try:
        # Verificar se o Stripe está configurado corretamente
        if not stripe.api_key:
            return Response(
                {'error': 'Stripe não está configurado corretamente. Verifique o arquivo .env e reinicie o servidor Django.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Buscar ou criar customer no Stripe
        customer_id = request.user.stripe_customer_id
        if customer_id:
            try:
                stripe.Customer.retrieve(customer_id, api_key=stripe_secret_key)
            except stripe.error.InvalidRequestError as e:
                if 'no such customer' in str(e).lower() or e.code == 'resource_missing':
                    customer_id = None
                    request.user.stripe_customer_id = None
                    request.user.save()

        if not customer_id:
            customer = stripe.Customer.create(
                email=request.user.email,
                name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                metadata={
                    'userId': str(request.user.id)
                },
                api_key=stripe_secret_key,
            )
            customer_id = customer.id
            request.user.stripe_customer_id = customer_id
            request.user.save()

        # Não há extras adicionais - fato já está incluído no preço de cada item

        # Criar sessão de checkout para pagamento único
        session = stripe.checkout.Session.create(
            api_key=stripe_secret_key,
            customer=customer_id,
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f"{settings.FRONTEND_URL}/success.html?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/catalogo.html",
            metadata={
                'userId': str(request.user.id),
                'type': 'booking',
                'packName': pack_name,
                'bookingDate': booking_date or '',
                'itemsCount': str(len(items) if items else '1'),
                'items': json.dumps(items) if items else json.dumps([{'packName': pack_name, 'packPrice': pack_price}])
            },
            allow_promotion_codes=True
        )

        return Response({
            'sessionId': session.id,
            'url': session.url
        })
    except stripe.error.StripeError as e:
        return Response(
            {'error': f'Erro do Stripe: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f'Erro ao criar checkout: {error_msg}')
        print(traceback.format_exc())
        return Response(
            {'error': f'Erro ao criar checkout: {error_msg}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_booking_from_session(request):
    """Confirmar reserva a partir do session_id do Stripe (chamado da página de success)"""
    stripe_secret_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
    
    if not stripe_secret_key:
        return Response(
            {'error': 'Chave do Stripe não configurada. Verifique o arquivo .env e reinicie o servidor Django.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    stripe.api_key = str(stripe_secret_key).strip()
    
    session_id = request.data.get('session_id')
    if not session_id:
        return Response(
            {'error': 'session_id é obrigatório'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Buscar sessão do Stripe
        session = stripe.checkout.Session.retrieve(session_id, api_key=stripe_secret_key)
        
        # Converter para dict para facilitar acesso
        payment_intent = session.payment_intent if hasattr(session, 'payment_intent') else session.get('payment_intent')
        
        # Verificar se já existe reserva para este payment_intent
        if payment_intent:
            existing_booking = Booking.objects.filter(
                stripe_payment_intent_id=payment_intent
            ).first()
            
            if existing_booking:
                return Response({
                    'message': 'Reserva já confirmada',
                    'booking_id': existing_booking.id
                })
        
        # Verificar se o pagamento foi concluído
        payment_status = session.payment_status if hasattr(session, 'payment_status') else session.get('payment_status')
        if payment_status != 'paid':
            return Response(
                {'error': 'Pagamento não foi concluído'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar se é do utilizador correto
        session_metadata = session.metadata if hasattr(session, 'metadata') else session.get('metadata', {})
        user_id_from_session = int(session_metadata.get('userId', 0))
        if user_id_from_session != request.user.id:
            return Response(
                {'error': 'Sessão não pertence a este utilizador'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Processar como no webhook
        handle_checkout_completed(session)
        
        return Response({
            'message': 'Reserva confirmada com sucesso',
            'session_id': session_id
        })
        
    except stripe.error.StripeError as e:
        return Response(
            {'error': f'Erro do Stripe: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        import traceback
        print(f'Erro ao confirmar reserva: {e}')
        print(traceback.format_exc())
        return Response(
            {'error': f'Erro ao confirmar reserva: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@require_POST
def webhook(request):
    """Webhook do Stripe para processar pagamentos"""
    # Garantir que a chave do Stripe está configurada
    stripe_secret_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
    
    if not stripe_secret_key:
        return HttpResponse(status=500)
    
    stripe_secret_key = str(stripe_secret_key).strip()
    
    if not stripe_secret_key or stripe_secret_key == '':
        return HttpResponse(status=500)
    
    # Configurar chave do Stripe antes de usar
    stripe.api_key = stripe_secret_key
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not webhook_secret:
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Processar apenas eventos de checkout completado
    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']
        session_id = session_obj.get('id', 'N/A')
        print(f'[WEBHOOK] checkout.session.completed recebido - Session ID: {session_id}')
        print(f'[WEBHOOK] Payment Status: {session_obj.get("payment_status", "N/A")}')
        print(f'[WEBHOOK] Metadata: {session_obj.get("metadata", {})}')
        handle_checkout_completed(session_obj)
        print(f'[WEBHOOK] Processamento concluído para Session ID: {session_id}')
    else:
        print(f'[WEBHOOK] Evento ignorado: {event["type"]}')

    return JsonResponse({'received': True})


def handle_checkout_completed(session):
    """Processar checkout completado - criar reserva(s)"""
    try:
        # Converter session object para dict se necessário
        if hasattr(session, 'mode'):
            session_mode = session.mode
            session_metadata = session.metadata or {}
            session_amount_total = session.amount_total
            session_payment_intent = session.payment_intent
        else:
            session_mode = session.get('mode')
            session_metadata = session.get('metadata', {})
            session_amount_total = session.get('amount_total')
            session_payment_intent = session.get('payment_intent')
        
        # Processar apenas reservas (pagamentos únicos)
        if session_mode == 'payment' and session_metadata.get('type') == 'booking':
            user_id = int(session_metadata.get('userId', 0))
            if user_id:
                user = User.objects.get(id=user_id)

                # Verificar se já existe reserva para este payment_intent
                if session_payment_intent:
                    existing = Booking.objects.filter(
                        stripe_payment_intent_id=session_payment_intent
                    ).exists()
                    if existing:
                        print(f'Reserva já existe para payment_intent: {session_payment_intent}')
                        return

                # Verificar se há múltiplos itens (do carrinho)
                items_json = session_metadata.get('items', '[]')
                booking_date = session_metadata.get('bookingDate') or None
                total_amount = session_amount_total / 100 if session_amount_total else 0
                
                try:
                    items = json.loads(items_json) if isinstance(items_json, str) else items_json
                except (json.JSONDecodeError, TypeError):
                    items = []
                
                # Se há múltiplos itens, criar uma reserva por item
                if items and len(items) > 1:
                    for item in items:
                        item_name = item.get('packName', '')
                        # Usar o preço do item (que já inclui o fato de proteção)
                        item_price = item.get('price', 0)
                        try:
                            item_price = float(item_price)
                        except (ValueError, TypeError):
                            # Se não tiver preço, dividir o total igualmente
                            item_price = total_amount / len(items)
                        
                        booking = Booking.objects.create(
                            user=user,
                            pack_name=item_name,
                            pack_price=item_price,
                            booking_date=booking_date,
                            addons='Fato de proteção incluído',
                            status='confirmed',
                            stripe_payment_intent_id=session_payment_intent
                        )
                        # Enviar emails de confirmação e recibo
                        from bookings.utils import send_booking_confirmation_email, send_booking_receipt_email
                        send_booking_confirmation_email(booking)
                        send_booking_receipt_email(booking)
                    print(f'Criadas {len(items)} reservas para user {user.email}')
                else:
                    # Item único ou usar packName do metadata
                    pack_name = session_metadata.get('packName', '')
                    if items and len(items) == 1:
                        pack_name = items[0].get('packName', pack_name)
                    
                    booking = Booking.objects.create(
                        user=user,
                        pack_name=pack_name,
                        pack_price=total_amount,
                        booking_date=booking_date,
                        addons='Fato de proteção incluído',
                        status='confirmed',
                        stripe_payment_intent_id=session_payment_intent
                    )
                    # Enviar emails de confirmação e recibo
                    from bookings.utils import send_booking_confirmation_email, send_booking_receipt_email
                    send_booking_confirmation_email(booking)
                    send_booking_receipt_email(booking)
                    print(f'Criada reserva para user {user.email}: {pack_name}')
    except User.DoesNotExist:
        print(f'Usuário não encontrado para userId: {session_metadata.get("userId")}')
    except Exception as e:
        import traceback
        print(f'Erro ao processar checkout: {e}')
        print(traceback.format_exc())
