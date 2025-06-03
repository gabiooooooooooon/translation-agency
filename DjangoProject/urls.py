from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('service.urls')),
    # path('', include('frontend.urls')),  # Добавили frontend
    path('', include('service.urls')),
    path('api/auth/', include('rest_framework.urls')),
    path('auth/token/logout/', auth_views.LogoutView.as_view(), name='logout')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
