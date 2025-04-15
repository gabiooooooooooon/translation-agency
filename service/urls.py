from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'consultations', ConsultationRequestViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),  # Эндпоинты для управления пользователями
    path('auth/', include('djoser.urls.authtoken')),  # Эндпоинты для токенов
]