from rest_framework.permissions import BasePermission


class IsAdminUserOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.userID or request.user.is_staff
