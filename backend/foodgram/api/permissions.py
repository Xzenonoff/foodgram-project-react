from rest_framework import permissions


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == user
            or user.is_staff is True
        )
