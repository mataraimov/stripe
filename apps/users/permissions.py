from rest_framework import permissions


class AnonPermission(permissions.BasePermission):
    message = "You are already authenticated"

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsVendorPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_Vendor



