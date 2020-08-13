""" rewrite the DRF filters module """
from __future__ import unicode_literals

import operator
import re
import sys
from functools import reduce

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.constants import LOOKUP_SEP
from django.template import loader
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from rest_framework.compat import distinct
from rest_framework.filters import BaseFilterBackend
from rest_framework.settings import api_settings

try:
    import coreapi
except ImportError:
    coreapi = None

try:
    import coreschema
except ImportError:
    coreschema = None


class DeepFilterBackend:
    """ 深入查询参数过滤器
    在 Django Rest Framework 中，支持以 queryset 的直接参数查询进行列表集的筛选
    在 DEFAULT_FILTER_BACKENDS 或者 ViewSet 的 filter_backends 中使用这个 DeepFilterBackend：

    'DEFAULT_FILTER_BACKENDS': (
        // ...
        'django_base.base_utils.filters.DeepFilterBackend',
    ),

    然后，在所有的 ListModelMixin 中，所有带有双下划线 `__` 的 querystring 参数，
    都会尝试在 queryset 中进行筛选。

    例如：

    ?user__username__startswith=admin_

    特殊处理：

    * 所有的 value 值如果是 True/False/None，会被转换成对应的 python 值
    * 如果查询参数前面带有 !，例如 `!name__startswith=a`，将使用 exclude 排除筛选条件而不是 filter

    为了安全起见，所有被捕获的查询条件参数，必须显式注册在对应的 View Class 的
    'allowed_deep_params' 列表里面，否则条件会被忽略并且获得一条警告。

    例如是的上述的两个条件生效：

    class UserViewSet(viewsets.ModelViewSet):
        # ...
        allowed_deep_params = ['user__username__startswith', 'name__starts__with']

    TODO: 考虑支持全部参数开放或者正则表达式过滤参数或者用户级别的权限控制
    TODO: 考虑添加静默选项以防止生产环境过多输出警告参数
    """

    request = None
    allowed_deep_params = []

    @staticmethod
    def never():
        """ todo """
        return Q(pk=None)

    @staticmethod
    def always():
        """ todo """
        return ~Q(pk=None)

    @staticmethod
    def get_setting_value(key, default):
        """ todo """
        if not hasattr(settings, key):
            return default
        return getattr(settings, key)

    def malformed_query(self):
        """ todo """
        # 配置 ALLOW_MALFORMED_QUERY = False 以实现非授权条件断路（返回空集）
        return self.always() if self.get_setting_value('ALLOW_MALFORMED_QUERY', True) \
            else self.never()

    def filter_queryset(self, request, queryset, view):
        """ todo """
        self.request = request
        self.allowed_deep_params = getattr(view, 'allowed_deep_params', ())

        # 注意，这个只能在 list 方法中生效，其他方法不作篡改
        if view.action != 'list':
            return queryset

        for key, val in request.query_params.items():
            if '__' in key:
                queryset = queryset.filter(self.get_single_condition_query(key, val))
            if key.startswith('_complex_query'):
                queryset = queryset.filter(self.parse_complex_query(val))

        if getattr(settings, 'REST_DEEP_DEFAULT_DISTINCT', None) \
                or request.query_params.get('~DISTINCT'):
            queryset = queryset.distinct()

        # 最后要加 distinct 去重
        return queryset

    def get_single_condition_query(self, key, val):
        """ todo """
        # 不满足的条件设置为条件短路
        if not re.match(r'^!*[A-Za-z0-9_]+$', key):
            print('!!!! Unsupported query phase: {}={}'.format(key, val), file=sys.stderr)
            return self.malformed_query()
        if key[0] == '!':
            return ~self.get_single_condition_query(key[1:], val)
        # 管理员登录可以豁免，否则所有的级联搜索必须显式放行
        if not self.get_setting_value('ALLOW_ALL_DEEP_PARAMS', False) \
                and not self.request.user.is_superuser \
                and key not in self.allowed_deep_params:
            print(
                '!!!! Deep filter param not registered: ' + key + '\n' +
                'The param is skipped, to make it work, '
                'add the params key name to `allowed_deep_params` list '
                'in the View class.\n!!!!', file=sys.stderr)
            return self.malformed_query()
        # 特殊字符串值映射
        value_mapper = {'False': False, 'True': True, 'None': None}
        val = value_mapper[val] if val in value_mapper else val
        # 如果是 id 列表类的入参，按照逗号进行分割
        if key.endswith('__in') and re.match(r'^(?:\d+,)*\d+$', val):
            val = map(int, val.split(','))
        elif key.endswith('__in') and re.match(r'^(?:[\d\w]+,)*[\d\w]+$', val):
            val = val.split(',')
        # 返回展开的条件
        return Q(**{key: val})

    def parse_complex_query(self, query):
        """ todo """
        if '||' in query:
            query_set = self.never()
            for part in query.split('||'):
                query_set |= self.parse_complex_query(part)
            return query_set
        if '&&' in query:
            query_set = self.always()
            for part in query.split('&&'):
                query_set &= self.parse_complex_query(part)
            return query_set
        tup = query.split('=')
        if len(tup) != 2:
            print('!!!! Unsupported query phase: {}'.format(query), file=sys.stderr)
            return self.malformed_query()
        return self.get_single_condition_query(*tup)  # tup=(key,val)

    def get_schema_fields(self, view):
        """ todo """
        # This is not compatible with widgets where the query param differs from the
        # filter's attribute name. Notably, this includes `MultiWidget`, where query
        # params will be of the format `<name>_0`, `<name>_1`, etc...
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'

        return [
            coreapi.Field(
                name=field,
                required=False,
                location='query',
                # schema=self.get_coreschema_field(field)
                schema=coreschema.String(description='* 注册的 DeepFilter 查询参数')
            ) for field in getattr(view, 'allowed_deep_params', [])
        ]


class SearchFilter(BaseFilterBackend):
    """ todo """
    # The URL query parameter used for the search.
    search_param = api_settings.SEARCH_PARAM
    template = 'rest_framework/filters/search.html'
    lookup_prefixes = {
        '^': 'istartswith',
        '=': 'iexact',
        '@': 'search',
        '$': 'iregex',
    }
    search_title = _('Search')
    search_description = _('A search term.')

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, '')
        return params.replace(',', ' ').split()

    def construct_search(self, field_name):
        """ todo """
        lookup = self.lookup_prefixes.get(field_name[0])
        if lookup:
            field_name = field_name[1:]
        else:
            lookup = 'icontains'
        return LOOKUP_SEP.join([field_name, lookup])

    def must_call_distinct(self, queryset, search_fields):
        """
        Return True if 'distinct()' should be used to query the given lookups.
        """
        for search_field in search_fields:
            opts = queryset.model._meta
            if search_field[0] in self.lookup_prefixes:
                search_field = search_field[1:]
            parts = search_field.split(LOOKUP_SEP)
            for part in parts:
                field = opts.get_field(part)
                if hasattr(field, 'get_path_info'):
                    # This field is a relation, update opts to follow the relation
                    path_info = field.get_path_info()
                    opts = path_info[-1].to_opts
                    if any(path.m2m for path in path_info):
                        # This field is a m2m relation so we know we need to call distinct
                        return True
        return False

    def filter_queryset(self, request, queryset, view):
        """ todo """
        search_fields = getattr(view, 'search_fields', None)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(str(search_field))
            for search_field in search_fields
        ]

        base = queryset
        conditions = []
        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            conditions.append(reduce(operator.or_, queries))
        queryset = queryset.filter(reduce(operator.and_, conditions))

        if self.must_call_distinct(queryset, search_fields):
            # Filtering against a many-to-many field requires us to
            # call queryset.distinct() in order to avoid duplicate items
            # in the resulting queryset.
            # We try to avoid this if possible, for performance reasons.
            queryset = distinct(queryset, base)
        return queryset

    def to_html(self, request, queryset, view):
        """ todo """
        if not getattr(view, 'search_fields', None):
            return ''

        term = self.get_search_terms(request)
        term = term[0] if term else ''
        context = {
            'param': self.search_param,
            'term': term
        }
        template = loader.get_template(self.template)
        return template.render(context)

    def get_schema_fields(self, view):
        """ todo """
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.search_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(self.search_title),
                    description=force_text(self.search_description)
                )
            )
        ]


class OrderingFilter(BaseFilterBackend):
    """
    改编自 rest_framework.filters.OrderingFilter，由于过于严格的过滤，导致不能支持级联字段的排序，例如
    ordering=-related_item__name 的过滤，在这里将过滤的逻辑剔除，以使得功能增强。
    """
    # The URL query parameter used for the ordering.
    ordering_param = api_settings.ORDERING_PARAM
    ordering_fields = None
    ordering_title = _('Ordering')
    ordering_description = _('Which field to use when ordering the results.')
    template = 'rest_framework/filters/ordering.html'

    def get_ordering(self, request, queryset, view):
        """
        Ordering is set by a comma delimited ?ordering=... query parameter.

        The `ordering` query parameter can be overridden by setting
        the `ordering_param` value on the OrderingFilter or by
        specifying an `ORDERING_PARAM` value in the API settings.
        """
        params = request.query_params.get(self.ordering_param)
        if params:
            fields = [param.strip() for param in params.split(',')]
            return fields
            # ordering = self.remove_invalid_fields(queryset, fields, view, request)
            # if ordering:
            #     return ordering

        # No ordering was included, or all the ordering fields were invalid
        return self.get_default_ordering(view)

    def get_default_ordering(self, view):
        """ todo """
        ordering = getattr(view, 'ordering', None)
        if isinstance(ordering, str):
            return (ordering,)
        return ordering

    # def get_default_valid_fields(self, queryset, view, context={}):
    #     # If `ordering_fields` is not specified, then we determine a default
    #     # based on the serializer class, if one exists on the view.
    #     if hasattr(view, 'get_serializer_class'):
    #         try:
    #             serializer_class = view.get_serializer_class()
    #         except AssertionError:
    #             # Raised by the default implementation if
    #             # no serializer_class was found
    #             serializer_class = None
    #     else:
    #         serializer_class = getattr(view, 'serializer_class', None)
    #
    #     if serializer_class is None:
    #         msg = (
    #             "Cannot use %s on a view which does not have either a "
    #             "'serializer_class', an overriding 'get_serializer_class' "
    #             "or 'ordering_fields' attribute."
    #         )
    #         raise ImproperlyConfigured(msg % self.__class__.__name__)
    #
    #     return [
    #         (field.source.replace('.', '__') or field_name, field.label)
    #         for field_name, field in serializer_class(context=context).fields.items()
    #         if not getattr(field, 'write_only', False) and not field.source == '*'
    #     ]
    #
    # def get_valid_fields(self, queryset, view, context={}):
    #     valid_fields = getattr(view, 'ordering_fields', self.ordering_fields)
    #
    #     if valid_fields is None:
    #         # Default to allowing filtering on serializer fields
    #         return self.get_default_valid_fields(queryset, view, context)
    #
    #     elif valid_fields == '__all__':
    #         # View explicitly allows filtering on any model field
    #         valid_fields = [
    #             (field.name, field.verbose_name) for field in queryset.model._meta.fields
    #         ]
    #         valid_fields += [
    #             (key, key.title().split('__'))
    #             for key in queryset.query.annotations
    #         ]
    #     else:
    #         valid_fields = [
    #             (item, item) if isinstance(item, six.string_types) else item
    #             for item in valid_fields
    #         ]
    #
    #     return valid_fields

    # def remove_invalid_fields(self, queryset, fields, view, request):
    #     valid_fields = [item[0] for item in self.get_valid_fields(queryset, view,
    #  {'request': request})]
    #     return [term for term in fields if term.lstrip('-') in
    # valid_fields and ORDER_PATTERN.match(term)]

    def filter_queryset(self, request, queryset, view):
        """ todo """
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            return queryset.order_by(*ordering)

        return queryset

    def get_template_context(self, request, queryset, view):
        """ todo """
        current = self.get_ordering(request, queryset, view)
        current = None if not current else current[0]
        options = []
        context = {
            'request': request,
            'current': current,
            'param': self.ordering_param,
        }
        # for key, label in self.get_valid_fields(queryset, view, context):
        #     options.append((key, '%s - %s' % (label, _('ascending'))))
        #     options.append(('-' + key, '%s - %s' % (label, _('descending'))))
        context['options'] = options
        return context

    def to_html(self, request, queryset, view):
        """ todo """
        template = loader.get_template(self.template)
        context = self.get_template_context(request, queryset, view)
        return template.render(context)

    def get_schema_fields(self, view):
        """ todo """
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.ordering_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(self.ordering_title),
                    description=force_text(self.ordering_description)
                )
            )
        ]
