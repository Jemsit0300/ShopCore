from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsAdminOrOwner(BasePermission):
    """Admin tüm siparişleri görebilir, user sadece kendi siparişlerini görebilir"""
    
    def has_object_permission(self, request, view, obj):
        # Admin tüm siparişleri görebilir
        if request.user and request.user.is_staff:
            return True
        # User sadece kendi siparişlerini görebilir
        return obj.user == request.user