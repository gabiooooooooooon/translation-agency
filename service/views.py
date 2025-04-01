from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import *
from .serializers import *
from .permissions import *

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ConsultationRequestViewSet(viewsets.ModelViewSet):
    queryset = ConsultationRequest.objects.all()
    serializer_class = ConsultationRequestSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]  # Только админ может управлять пользователями


class ConsultationRequestViewSet(viewsets.ModelViewSet):
    queryset = ConsultationRequest.objects.all()
    serializer_class = ConsultationRequestSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]  # Анонимы могут создавать
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsTranslator | IsAdmin]  # Редактировать могут только переводчики и админы
        return [permissions.IsAuthenticated()]  # Просмотр для авторизованных


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsClient]  # Только клиенты могут оставлять отзывы
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsClientOwnerOrReadOnly]  # Редактировать может только автор
        return [permissions.AllowAny()]  # Просмотр для всех


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer  # (Нужно создать, см. ниже)

    def get_permissions(self):
        if self.action == 'create':
            return [IsClient]  # Создавать могут только клиенты
        elif self.action in ['update', 'partial_update']:
            return [CanEditOrder]  # Редактирование по спец.правилам
        return [permissions.IsAuthenticated()]  # Просмотр для авторизованных

    def perform_create(self, serializer):
        if self.request.user.role == 'client':
            serializer.save(user=self.request.user)
