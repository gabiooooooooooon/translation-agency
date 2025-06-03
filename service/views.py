import json
import logging
import os
import uuid

from django.contrib.auth.views import LoginView, TemplateView
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.uploadhandler import TemporaryFileUploadHandler, MemoryFileUploadHandler
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse, QueryDict
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from .serializers import *
from .permissions import *
from django.shortcuts import render
from django.views.decorators.cache import never_cache

def services_written(request):
    return render(request, 'services_written.html')

class CustomLoginView(LoginView):
    template_name = 'auth.html'
    redirect_authenticated_user = True

logger = logging.getLogger(__name__)

class PasswordResetView(TemplateView):
    template_name = 'password_reset.html'

@require_POST
def submit_order(request):
    try:
        # Настройка обработчиков загрузки файлов
        request.upload_handlers = [TemporaryFileUploadHandler(), MemoryFileUploadHandler()]

        # Проверка аутентификации
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        # Разные обработчики для JSON и form-data
        if request.content_type == 'application/json':
            try:
                data = request.data  # Для DRF APIView
            except AttributeError:
                data = json.loads(request.body.decode('utf-8'))
            files = {}
        else:
            data = request.POST
            files = request.FILES

        # Валидация обязательных полей
        required_fields = ['service_type', 'source_language', 'target_language']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse(
                {'error': f'Missing required fields: {", ".join(missing_fields)}'},
                status=400
            )

        try:
            service = Service.objects.get(category=data['service_type'])
        except Service.DoesNotExist:
            return JsonResponse({'error': 'Service not found'}, status=404)

        # Создание заказа в транзакции
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                service=service,
                from_language=data['source_language'],
                to_language=data['target_language'],
                comment=data.get('comment', ''),
                delivery_method=data.get('delivery_type', 'pickup'),
                address=data.get('delivery_address', ''),
                total_price=service.min_price
            )

            # Обработка файлов
            if 'document_file' in files:
                file = files['document_file']
                if isinstance(file, (InMemoryUploadedFile, TemporaryUploadedFile)):
                    try:
                        Document.objects.create(order=order, file=file)
                    except Exception as e:
                        logger.error(f"File upload failed: {str(e)}")
                        raise

            # Обработка дополнительных услуг
            service_options = {
                'notarization': ('Нотариальное заверение', 700),
                'apostille': ('Апостиль', 3500)
            }

            for option_key, (option_name, default_price) in service_options.items():
                if data.get(option_key) == 'true':
                    try:
                        option = OrderOption.objects.get(name=option_name)
                        OrderOptionSelection.objects.create(
                            order=order,
                            option=option,
                            quantity=1
                        )
                        order.total_price += option.price
                    except OrderOption.DoesNotExist:
                        order.total_price += default_price
                        logger.warning(f"Option {option_name} not found, using default price")

            order.save()

        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'total_price': order.total_price
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Order creation failed: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

class CustomUserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {'detail': 'User created successfully'},
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        # Создаем заказ
        order_data = {
            'user': request.user.id,
            'service': Service.objects.get(category=request.POST.get('service_type')).id,
            'from_language': request.POST.get('source_language'),
            'to_language': request.POST.get('target_language'),
            'comment': request.POST.get('comment', ''),
            'delivery_method': request.POST.get('delivery_type', 'pickup'),
            'address': request.POST.get('delivery_address', ''),
            'total_price': request.POST.get('total_price', 0),
        }

        serializer = OrderSerializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # Обрабатываем файл
        if 'document' in request.FILES:
            file = request.FILES['document']
            ext = os.path.splitext(file.name)[1]
            new_filename = f"order_{order.id}_{uuid.uuid4()}{ext}"

            file_path = default_storage.save(f'orders/{new_filename}', file)

            Document.objects.create(
                order=order,
                file=file_path
            )

        # Обрабатываем доп. услуги
        if request.POST.get('notarization') == 'true':
            option = OrderOption.objects.get(name='Нотариальное заверение')
            order.options.add(option, through_defaults={'quantity': 1})

        if request.POST.get('apostille') == 'true':
            option = OrderOption.objects.get(name='Апостиль')
            order.options.add(option, through_defaults={'quantity': 1})

        return Response(OrderSerializer(order).data)

    except Exception as e:
        return Response({'error': str(e)}, status=400)

@never_cache
def order_page(request):
    services = Service.objects.all()
    options = OrderOption.objects.all()
    return render(request, 'order.html', {
        'services': services,
        'options': options
    })


@api_view(['POST'])
def submit_order(request):
    try:
        data = json.loads(request.body)

        # Подготовка данных для сериализатора
        order_data = {
            'service': data.get('serviceType'),
            'from_language': data.get('sourceLanguage'),
            'to_language': data.get('targetLanguage'),
            'comment': data.get('comment', ''),
            'delivery_method': data.get('deliveryType', 'pickup'),
            'address': data.get('deliveryAddress', ''),
            'total_price': float(data.get('totalPrice', 0).replace(' р.', '')),
            'options': [],
            'documents': []
        }

        # Обработка файлов
        if 'documentFile' in request.FILES:
            order_data['documents'].append({
                'file': request.FILES['documentFile']
            })

        # Обработка доп. услуг
        if data.get('notarization') == 'true':
            order_data['options'].append({
                'option': 'notarization',
                'quantity': 1
            })

        if data.get('apostille') == 'true':
            order_data['options'].append({
                'option': 'apostille',
                'quantity': 1
            })

        serializer = OrderSerializer(data=order_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'order_id': serializer.instance.id})
        return Response({'errors': serializer.errors}, status=400)

    except Exception as e:
        return Response({'error': str(e)}, status=500)

@require_POST
@never_cache
def logout_view(request):
    from django.contrib.auth import logout
    logout(request)

    response = HttpResponseRedirect('/')
    # Жесткие заголовки против кэширования
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = 'Fri, 01 Jan 1990 00:00:00 GMT'

    # Очистка сессионных cookies
    response.delete_cookie('sessionid')
    response.delete_cookie('csrftoken')

    return response

def order_success(request):
    order_id = request.GET.get('order_id')
    return render(request, 'services_order_success.html', {'order_id': order_id})
def index(request):
    return render(request, 'index.html')  # рендерим HTML

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