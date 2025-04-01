from django.contrib import admin
from .models import *

# Регистрируем стандартные модели Django
admin.site.register(User)

# Кастомизация отображения для ConsultationRequest
@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'phone', 'email', 'status', 'created_at')
    list_filter = ('type', 'status')
    search_fields = ('phone', 'email')

# Регистрируем остальные модели с базовыми настройками
admin.site.register(Review)
admin.site.register(Service)
admin.site.register(OrderOption)
admin.site.register(Order)
admin.site.register(OrderOptionSelection)
admin.site.register(Document)