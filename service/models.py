from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Клиент'),
        ('translator', 'Переводчик'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        swappable = 'AUTH_USER_MODEL'


class ConsultationRequest(models.Model):
    TYPE_CHOICES = [
        ('call', 'Звонок'),
        ('email', 'Почта'),
    ]
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processed', 'Обработан'),
    ]
    type = models.CharField(max_length=5, choices=TYPE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Service(models.Model):
    CATEGORY_CHOICES = [
        ('oral', 'Устный перевод'),
        ('written', 'Письменный перевод'),
        ('additional', 'Доп. услуги'),
    ]
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=255)
    description = models.TextField()
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderOption(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    LANGUAGE_CHOICES = [
        ('ru', 'Русский'),
        ('en', 'Английский'),
        ('es', 'Испанский'),
        ('fr', 'Французский'),
        ('de', 'Немецкий'),
        ('zh', 'Китайский'),
        ('other', 'Другой'),
    ]
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('in_progress', 'В работе'),
        ('ready', 'Готово'),
        ('sent', 'Отправлено'),
        ('received', 'Получено'),
        ('rejected', 'Отказ'),
    ]
    DELIVERY_CHOICES = [
        ('pickup', 'Самовывоз'),
        ('delivery', 'Доставка'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='pending')
    from_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    to_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    comment = models.TextField(blank=True)
    delivery_method = models.CharField(max_length=8, choices=DELIVERY_CHOICES, default='pickup')
    address = models.CharField(max_length=255, default='1')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    options = models.ManyToManyField(OrderOption, through='OrderOptionSelection')


class OrderOptionSelection(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    option = models.ForeignKey(OrderOption, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)


class Document(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    file = models.FileField(upload_to='order_documents/')
    created_at = models.DateTimeField(auto_now_add=True)