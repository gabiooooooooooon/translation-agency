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

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role in ['admin', 'translator']:
            return ConsultationRequest.objects.all()  # Админы и переводчики видят все
        return ConsultationRequest.objects.filter(email=user.email)  # Клиенты видят только свои

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]  # Анонимы могут создавать
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsTranslator(), IsAdmin()]  # Только переводчики и админы редактируют
        return [permissions.IsAuthenticated()]  # Авторизованные могут просматривать


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsClient()]  # Только клиенты могут оставлять отзывы
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsClientOwnerOrReadOnly()]  # Редактировать может только автор
        return [permissions.AllowAny()]  # Просмотр для всех


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        # Проверяем, есть ли consultation_request_id в запросе
        consultation_request_id = request.data.get('consultation_request_id')
        if not consultation_request_id:
            return Response(
                {"error": "consultation_request_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            consultation = ConsultationRequest.objects.get(id=consultation_request_id)
        except ConsultationRequest.DoesNotExist:
            return Response(
                {"error": "Consultation request not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Собираем данные для Order
        order_data = {
            'user': request.user.id,
            'service': request.data.get('service'),  # Должен быть передан явно
            'from_language': request.data.get('from_language'),
            'to_language': request.data.get('to_language'),
            'comment': request.data.get('comment', ''),
            'delivery_method': request.data.get('delivery_method', 'pickup'),
            'address': request.data.get('address', ''),
            'total_price': request.data.get('total_price', 0),
        }

        serializer = OrderSerializer(data=order_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role in ['admin', 'translator']:
            return Order.objects.all()  # Исправлено: возвращаем Order, а не ConsultationRequest
        return Order.objects.filter(user=user)  # Клиенты видят только свои заказы

    def get_permissions(self):
        if self.action == 'create':
            return [IsClient()]
        elif self.action in ['update', 'partial_update']:
            return [CanEditOrder()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)