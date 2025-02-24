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
        if view.action == 'retrieve':
            return True

        return request.user.is_staff or obj == request.user
