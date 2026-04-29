from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfileOwner(BasePermission):
    """Permite acceder solo al perfil del usuario autenticado."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.user == request.user


class IsOwner(BasePermission):
    """Permite acceder solo a objetos cuyo campo user coincide."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and getattr(obj, "user", None) == request.user


class IsDailyRecordOwner(BasePermission):
    """Permite acceder solo si el daily_record pertenece al usuario autenticado."""

    def has_object_permission(self, request, view, obj):
        daily_record = getattr(obj, "daily_record", None)
        return (
            request.user.is_authenticated
            and daily_record is not None
            and daily_record.user == request.user
        )


class IsStaffOrReadOnly(BasePermission):
    """Permite solo lectura a usuarios normales; escritura solo a staff."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff
