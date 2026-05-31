from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """Allow read to anyone, write only to admin users."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.user_role == 'admin'

class IsSellerOrAdmin(BasePermission):
    """Only sellers and admins can create/update/delete."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.user_role in ['seller', 'admin']

class IsOwnerOrAdmin(BasePermission):
    """Object-level permission: only the owner (user who created) or an admin can access."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.user_role == 'admin':
            return True
        # Assumes obj has a 'user' attribute
        return obj.user == request.user

class IsSellerOwnerOrAdmin(BasePermission):
    """For Product: seller who owns the product or admin can edit."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.user_role == 'admin':
            return True
        return obj.seller == request.user

class IsOrderOwnerOrAdmin(BasePermission):
    """For Order: the user who placed the order or an admin."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.user_role == 'admin':
            return True
        return obj.user == request.user