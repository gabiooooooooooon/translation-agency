from rest_framework import serializers
from .models import *
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class ConsultationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationRequest
        fields = '__all__'

class OrderOptionSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderOptionSelection
        fields = ['option', 'quantity']

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['file']

class OrderSerializer(serializers.ModelSerializer):
    options = OrderOptionSelectionSerializer(many=True, write_only=True)  # Вложенные опции
    documents = DocumentSerializer(many=True, write_only=True)  # Вложенные файлы
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user']  # Запрещаем передавать user вручную

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user  # Автоподстановка
        return super().create(validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Показывает имя пользователя
    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']  # Эти поля нельзя менять при создании

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'password', 'role', 'phone')
