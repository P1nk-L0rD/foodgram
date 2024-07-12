from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Права доступа для автора и админов."""

    def has_permission(self, request, view):
        return (request.method
                in permissions.SAFE_METHODS
                or request.user.is_authenticated
                or request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        return (request.method
                in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_staff)
