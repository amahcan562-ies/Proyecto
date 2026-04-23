from rest_framework.permissions import BasePermission


class IsProfileOwner(BasePermission):
    """Permite acceder solo al perfil del usuario autenticado."""

    def has_object_permission(self, request, view, obj):
        return
        (request.user.is_authenticated and return request.user.is_authenticated and obj.user == request.user

