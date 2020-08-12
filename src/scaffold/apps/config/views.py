from django.contrib.contenttypes.models import ContentType
from django.db.models.base import ModelBase
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from scaffold import utils as u

from . import models as m
from . import serializers as s


class OptionViewSet(viewsets.GenericViewSet):
    queryset = m.Option.objects.all()
    serializer_class = s.OptionSerializer
    filter_fields = '__all__'

    @action(methods=['GET'], detail=False)
    def get_all(self, request):
        return Response(m.Option.get_all())

    @action(methods=['GET'], detail=False)
    def get(self, request):
        return Response(m.Option.get(request.query_params.get('key')))

    @action(methods=['POST'], detail=False)
    def set(self, request):
        m.Option.set(request.data.get('key'), request.data.get('value'))
        return u.http.response_success('设置成功', silent=True)

    @action(methods=['GET'], detail=False)
    def choices(self, request):
        """ 返回所有的常量选项 """
        from django.apps import apps
        result = dict()

        def inspect_class(cls):
            if type(cls) != ModelBase or cls.__name__ in result or not hasattr(cls, '_meta'):
                return
            section = dict()
            if not cls._meta.abstract:
                section['content_type_id'] = ContentType.objects.get_for_model(cls).id
            if hasattr(cls, '__doc__'):
                section['help_text'] = cls.__doc__
            for attr_name, attr in cls.__dict__.items():
                # print(cls.__name__, attr_name, attr)
                if attr_name.endswith('_CHOICES'):
                    section[attr_name.replace('_CHOICES', '').lower()] = dict(attr)
            result[cls.__name__] = section
            # 深入解析所有的 abstract base class
            for super_class in cls.__bases__:
                inspect_class(super_class)

        for app in apps.all_models.values():
            for cls in app.values():
                inspect_class(cls)
        return Response(result)


class VersionViewSet(viewsets.ModelViewSet):
    queryset = m.Version.objects.all()
    serializer_class = s.VersionSerializer
    filter_fields = '__all__'
    ordering = ['-pk']
