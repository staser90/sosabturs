"""
Views do chatbot (API usada pelo widget de chat).
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def chatbot_message(request):
    """Endpoint do chatbot. Aceita mensagem e devolve resposta (placeholder)."""
    if request.method == 'GET':
        return Response({'status': 'ok', 'message': 'Chatbot disponível'})
    message = request.data.get('message', '') if request.data else ''
    # Resposta simples; pode ser integrado com lógica ou API externa depois
    return Response({
        'reply': 'Obrigado pela sua mensagem. Em breve entraremos em contacto.' if message else 'Envie uma mensagem.',
        'received': message,
    }, status=status.HTTP_200_OK)
