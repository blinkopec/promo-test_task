from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Receipt
from .serializers import ReceiptSerializer

class ReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return Receipt.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors },
               status=status.HTTP_400_BAD_REQUEST, 
            )
        serializer.save()
        return Response({'success': True}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {'success': False, 'errors': 'Неверный логин или пароль'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    login(request,user)
    return Response({'success': True, 'username': user.username})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    logout(request)
    return Response({'success': True})

@api_view(['GET'])
@permission_classes([AllowAny])
def api_me(request):
    if not request.user.is_authenticated:
        return Response({'authenticated': False})
    return Response({
        'authenticated': True,
        'username': request.username,
        'is_staff': request.user.is_staff,
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_config(request):
    return Response({
        'promo_start': settings.PROMO_START_DATE,
        'promo_end': settings.PROMO_END_DATE,
    })

@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def api_csrf(request):
    return Response({'ok': True})