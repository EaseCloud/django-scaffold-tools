""" Extended rest_framework permissions classes """
import re
from logging import getLogger

from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS

logger = getLogger(__name__)


class ActionBasedPermission(BasePermission):
    """ ViewSet action level Permission integrator
    https://stackoverflow.com/a/47528633/2544762
    Grant or deny access to a view, based on a mapping in view.action_permissions

    Example:

        class MyModelViewSet(ReadOnlyModelViewSet):
            serializer_class = MyModelSerializer
            queryset = MyModel.objects.all()

            permission_classes = [ActionBasedPermission]
            action_permissions = {
                'list,retrieve': IsMember,
                'destroy': IsAdminUser,
                'create,update,partial_update':
                    HasPermissions.build('basic_info_admin'),
            }
    """

    def has_permission(self, request, view):
        for actions, cls in getattr(view, 'action_permissions', {}).items():
            # 支持 actions 是字符串或者数组，如果是字符串先转为数组
            if isinstance(actions, str):
                actions = re.split(r'\s+|[\.\|,]', actions)
            # 判断是当前 view 的动作是否在清单中
            if view.action in actions:
                return cls().has_permission(request, view)
        return True

    def has_object_permission(self, request, view, obj):
        for actions, cls in getattr(view, 'action_permissions', {}).items():
            # 支持 actions 是字符串或者数组，如果是字符串先转为数组
            if isinstance(actions, str):
                actions = re.split(r'\s+|[\.\|,]', actions)
            # 判断是当前 view 的动作是否在清单中
            if view.action in actions:
                return cls().has_object_permission(request, view, obj)
        return True


class IsAuthor(BasePermission):
    """ has permission if the current user is the author of the object """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


# TODO: Planning to deprecate in 1.0
class IsAdminOrIsSelf(BasePermission):
    """ has permission if the current user is the owner of the object or admin user """

    def has_object_permission(self, request, view, obj):
        logger.warning(
            'Do not use IsAdminOrIsSelf permission, '
            'use bitwise OR to compose IsAuthor and IsAdminUser instead.')
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
    perms = ()

    @classmethod
    def build(cls, *args):
        """ Derive a meta subclass of current by replacing the perms property. """
        return type(
            'HasPermissions',
            (cls,),
            dict(perms=tuple(p if '.' in p else f'{cls.app_label}.{p}' for p in args))
        )

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or any(request.user.has_perm(perm) for perm in self.perms)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
