"""
Views da app accounts: API de autenticação (JWT) e páginas HTML.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserRegistrationSerializer, UserSerializer

User = get_user_model()


# ----- API views (JSON, usadas por accounts/urls.py sob /api/auth/) -----

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Registo de utilizador. Devolve access e refresh token."""
    serializer = UserRegistrationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    # Email de boas-vindas (opcional)
    if getattr(settings, 'DEFAULT_FROM_EMAIL', None):
        try:
            send_mail(
                subject='Bem-vindo ao SO SAB',
                message='A sua conta foi criada com sucesso.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass
    refresh = RefreshToken.for_user(user)
    return Response({
        'user': UserSerializer(user).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login com username e password. Devolve access e refresh token."""
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response(
            {'error': 'username e password são obrigatórios'},
            status=status.HTTP_400_BAD_REQUEST
        )
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {'error': 'Credenciais inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    refresh = RefreshToken.for_user(user)
    return Response({
        'user': UserSerializer(user).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    """Faz blacklist do refresh token enviado no body."""
    refresh = request.data.get('refresh')
    if not refresh:
        return Response({'error': 'refresh token obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh)
        token.blacklist()
    except Exception:
        pass
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Devolve o utilizador autenticado (JWT)."""
    return Response({'user': UserSerializer(request.user).data})


@api_view(['POST', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Atualiza perfil do utilizador (first_name, last_name, email, etc.)."""
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response({'user': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Altera a senha do utilizador."""
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    if not old_password or not new_password:
        return Response(
            {'error': 'old_password e new_password são obrigatórios'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not request.user.check_password(old_password):
        return Response({'error': 'Senha atual incorreta'}, status=status.HTTP_400_BAD_REQUEST)
    request.user.set_password(new_password)
    request.user.save()
    # Email a avisar (opcional)
    if getattr(settings, 'DEFAULT_FROM_EMAIL', None):
        try:
            send_mail(
                subject='Senha alterada - SO SAB',
                message='A sua senha foi alterada com sucesso.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
            )
        except Exception:
            pass
    return Response({'message': 'Senha alterada com sucesso'})


@api_view(['GET'])
@permission_classes([AllowAny])
def logout_page(request):
    """Redireciona para a página inicial (usado após logout)."""
    return redirect('/')


# ----- Páginas HTML (usadas por tours_saas/urls.py quando DEBUG) -----

def login_page(request):
    """Página de login (template login.html)."""
    return render(request, 'login.html')


def dashboard_page(request):
    """Página do dashboard (template dashboard.html)."""
    return render(request, 'dashboard.html')


def profile_page(request):
    """Página de perfil (template profile.html)."""
    return render(request, 'profile.html')
