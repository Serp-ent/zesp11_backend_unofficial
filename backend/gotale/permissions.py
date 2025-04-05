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


class isAuthenticatedOrAdmin(permissions.BasePermission):
    """Allow everyone to read, let authenticated users create, and admins do everything."""

    def has_permission(self, request, view):
        # Admin bypass: staff users can perform any action.
        if request.user.is_staff:
            return True

        # Everyone can read.
        if view.action in permissions.SAFE_METHODS:
            return True

        # Only authenticated users can create games.
        if view.action == "create":
            return request.user.is_authenticated

        # Only admins can destroy (handled by admin bypass above).
        if view.action == "destroy":
            return False

        # Default to allowing the action.
        return True


class IsInGame(permissions.BasePermission):
    """Allow only users with an active session in the game (or admins)."""

    def has_object_permission(self, request, view, obj):
        # Admin bypass: allow admins.
        if request.user.is_staff:
            return True

        # Check if the user has an active session in this game.
        return obj.sessions.filter(game__user=request.user, is_active=True).exists()
