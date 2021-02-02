""" Extended rest_framework permissions classes """
from django.conf import settings
from rest_framework.permissions import *


class ActionBasedPermission(AllowAny):
    """ ViewSet action level Permission integrator
    https://stackoverflow.com/a/47528633/2544762
    Grant or deny access to a view, based on a mapping in view.action_permissions

    Example:

        class MyModelViewSet(ReadOnlyModelViewSet):
            serializer_class = MyModelSerializer
            queryset = MyModel.objects.all()

            permission_classes = (ActionBasedPermission,)
            action_permissions = {
                IsAuthenticated: ['update', 'partial_update', 'destroy', 'list', 'create'],
                AllowAny: ['retrieve']
            }

            authentication_classes = (TokenAuthentication, SessionAuthentication)
    """

    def has_permission(self, request, view):
        for cls, actions in getattr(view, 'action_permissions', {}).items():
            if view.action in actions:
                return cls().has_permission(request, view)
        return False


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


class HasPermissions(BasePermission):
    """ check if user has a specific django permission

    Example:

        class MyModelViewSet(ReadOnlyModelViewSet):
            serializer_class = MyModelSerializer
            queryset = MyModel.objects.all()

            permission_classes = (
                HasPermissions.build('core.sales_manager', 'core.user_manager'),
            )

    """
    # if no app name specified, e.g. 'my_permission' rather than 'myapp.my_permissions',
    # a default app label will be added, you can set another app in setting as needed.
    app_label = getattr(settings, 'DEFAULT_PERMISSION_APP', 'core')

    def __init__(self):
        self.perms = []

    @classmethod
    def build(cls, *args):
        perm = cls()
        perm.perms = \
            [p if '.' in p else f'{cls.app_label}.{p}' for p in args]
        return perm

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.has_perms(self.perms)
