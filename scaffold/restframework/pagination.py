""" Custom specified pagination classes """
from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response


class PageNumberPagination(pagination.PageNumberPagination):
    """ 自定义分页器
    基于 rest_framework 的 PageNumberPagination 基础上修改
    """
    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('pages', self.page.paginator.num_pages),
            # ('next', self.get_next_link()),
            # ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                # page_size 传入空字符串，0 或者负数时，返回所有内容（依然保留分页格式）
                if not request.query_params[self.page_size_query_param] or \
                        int(request.query_params[self.page_size_query_param]) <= 0:
                    return 1e100
                # 原始的 rest_framework 实现
                return pagination._positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size
