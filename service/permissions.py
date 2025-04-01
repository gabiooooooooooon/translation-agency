from rest_framework import permissions

class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'client'

class IsTranslator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'translator'

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsClientOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class CanEditOrder(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'translator' or request.user.role == 'admin':
            return True
        # Клиент может редактировать только при создании (статус "на рассмотрении")
        if request.user.role == 'client' and obj.status == 'pending' and obj.user == request.user:
            return True
        return False