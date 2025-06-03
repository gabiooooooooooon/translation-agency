from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)

from .views import CustomLoginView, PasswordResetView

# Импортируем views напрямую, без моделей
from .views import index, services_written, submit_order

router = DefaultRouter()


# Ленивая регистрация ViewSets
def get_user_viewset():
    from .views import UserViewSet
    return UserViewSet


def get_consultation_viewset():
    from .views import ConsultationRequestViewSet
    return ConsultationRequestViewSet


def get_review_viewset():
    from .views import ReviewViewSet
    return ReviewViewSet


def get_order_viewset():
    from .views import OrderViewSet
    return OrderViewSet


router.register(r'users', get_user_viewset())
router.register(r'consultations', get_consultation_viewset())
router.register(r'reviews', get_review_viewset())
router.register(r'orders', get_order_viewset(), basename='order')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/token/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('auth/users/reset_password/', include('djoser.urls.jwt')),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('reset_password/', PasswordResetView.as_view(), name='password_reset'),

    path('api/', include(router.urls)),
    path('', index, name='index'),
    path('services/written/', services_written, name='services_written'),
path('submit_order/', submit_order, name='submit_order'),
    path(
        'services/order/',
        TemplateView.as_view(template_name='services_order.html'),
        name='services_order'
    ),
]