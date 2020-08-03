""" Extended rest_framework permissions classes """
from rest_framework.permissions import *


class IsAdminOrIsSelf(BasePermission):
    """ has permission if the current user is the owner of the object or admin user """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or \
               request.user.is_staff or \
               request.user.is_superuser


class IsAdminOrReadOnly(BasePermission):
    """ has permission only if the current user is admin """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or \
               request.user and (request.user.is_staff or request.user.is_superuser)


