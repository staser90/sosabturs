from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import stripe
from .models import Subscription
from .serializers import SubscriptionSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_subscription(request):
    """Obter assinatura atual do usuário"""
    subscription = Subscription.objects.filter(
        user=request.user,
        status__in=['active', 'trialing']
    ).order_by('-created_at').first()

    if not subscription:
        return Response({'subscription': None})

    # Buscar detalhes atualizados do Stripe
    try:
        stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
        serializer = SubscriptionSerializer(subscription)
        data = serializer.data
        data['stripe_data'] = {
            'status': stripe_subscription.status,
            'current_period_end': stripe_subscription.current_period_end,
            'cancel_at_period_end': stripe_subscription.cancel_at_period_end
        }
        return Response({'subscription': data})
    except Exception as e:
        serializer = SubscriptionSerializer(subscription)
        return Response({'subscription': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """Cancelar assinatura"""
    subscription = Subscription.objects.filter(
        user=request.user,
        status__in=['active', 'trialing']
    ).order_by('-created_at').first()

    if not subscription:
        return Response(
            {'error': 'Nenhuma assinatura ativa encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        # Cancelar no Stripe (no final do período)
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )

        # Atualizar no banco
        subscription.cancel_at_period_end = True
        subscription.save()

        return Response({'message': 'Assinatura será cancelada no final do período atual'})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reactivate_subscription(request):
    """Reativar assinatura cancelada"""
    subscription = Subscription.objects.filter(
        user=request.user,
        cancel_at_period_end=True
    ).order_by('-created_at').first()

    if not subscription:
        return Response(
            {'error': 'Nenhuma assinatura para reativar encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        # Reativar no Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=False
        )

        # Atualizar no banco
        subscription.cancel_at_period_end = False
        subscription.save()

        return Response({'message': 'Assinatura reativada com sucesso'})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_portal_session(request):
    """Criar sessão do portal do cliente Stripe"""
    if not request.user.stripe_customer_id:
        return Response(
            {'error': 'Cliente Stripe não encontrado'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        session = stripe.billing_portal.Session.create(
            customer=request.user.stripe_customer_id,
            return_url=f"{settings.FRONTEND_URL}/dashboard.html",
        )
        return Response({'url': session.url})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
