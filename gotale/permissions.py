from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow list, create, and destroy only for admins
        if view.action in ["list", "retrieve"]:
            return True

        if view.action in ["create", "destroy"]:
            return request.user.is_staff
        # Allow retrieve, update, partial_update for authenticated users
        elif view.action in ["update", "partial_update"]:
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        # Check if the user is admin or the object owner for retrieve/update
        if view.action == "retrieve":
            return True

        return request.user.is_staff or obj == request.user


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only the owner or an admin to edit/delete a scenario.
    Read Only otherwise
    """

    def has_object_permission(self, request, view, obj):
        # Allow read permissions to anyone (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user or request.user.is_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ["list", "retrieve"]:
            return True

        user = request.user
        return user.is_authenticated and user.is_staff

    def has_object_permission(self, request, view, obj):
        if view.action == "retrieve":
            return True

        return True
