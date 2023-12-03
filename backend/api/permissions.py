from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """Изменения доступны при наличии прав администратора."""

    message = 'Отсутствуют права админитсратора!'

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.is_admin
        )


class AuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
