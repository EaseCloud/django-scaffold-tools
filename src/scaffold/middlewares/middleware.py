from django.conf import settings
from threading import currentThread
from django.utils.deprecation import MiddlewareMixin

_requests = {}


def get_request():
    return _requests[currentThread()]


class GlobalRequestMiddleware(MiddlewareMixin):
    """ 将 request 对象置于线程中可以供任意位置访问
    """

    @staticmethod
    def process_request(request):
        _requests[currentThread()] = request


class CustomExceptionMiddleware(MiddlewareMixin):
    """ 当捕获到 APIError 时自动包装响应一个错误的 HTTP 响应
    """

    @staticmethod
    def process_exception(request, exception):
        import traceback
        from django.http import JsonResponse
        from sys import stderr
        from django.conf import settings
        from django.core.exceptions import ValidationError
        # Retrieves the error message, response error message only.
        msg = exception.message if hasattr(exception, 'message') else str(exception)
        # Bypass the exception raised but still print to stderr
        if settings.DEBUG or type(exception) not in [AssertionError, ValidationError]:
            print(traceback.format_exc(), file=stderr)
        # Return a client-recognizable format.
        return JsonResponse(dict(
            ok=False,
            msg=msg
        ), status=400)


# class SingleSessionMiddleware(MiddlewareMixin):
#     def process_response(self, request, response):
#         from django.contrib.auth import logout
#         # from django.http import JsonResponse
#         # print(request.user.base_member.session_key)
#         # print(request.session.session_key)
#         if hasattr(request.user, 'base_member') and \
#                 request.user.base_member.session_key != \
#                 request.session.session_key and \
#                 request.get_full_path() != '/api/option/get_guide_image/' and \
#                 request.user.base_member.session_key:
#             import json
#             content_string = str(response.content, encoding="utf8")
#             dict_content = json.loads(content_string)
#             dict_content['force_logout'] = 1
#             response.content = bytes(json.dumps(dict_content), encoding="utf-8")
#             # print(content_string)
#             # print(response.content)
#             # print(response)
#             # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
#             return response
#         # if request.user.is_anonymous:
#         #     response['FORCE_LOGOUT'] = '1'
#         return response


class FullMediaUrlMiddleware(MiddlewareMixin):
    """ 在 MediaUrl 中自动拼接完整的 request 路径 """
    @staticmethod
    def process_request(request):
        from django.conf import settings
        from urllib.parse import urljoin
        settings.MEDIA_URL = \
            urljoin(request.get_raw_uri(), settings.MEDIA_URL)
        settings.STATIC_URL = \
            urljoin(request.get_raw_uri(), settings.STATIC_URL)
        # settings.ALIPAY_NOTIFY_URL = \
        #     urljoin(request.get_raw_uri(), settings.ALIPAY_NOTIFY_URL)


#
#
# class CookieCsrfMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         csrftoken = request.COOKIES.get('csrftoken')
#         if csrftoken:
#             request.META['HTTP_X_CSRFTOKEN'] = csrftoken


class ExplicitSessionMiddleware(MiddlewareMixin):
    """ 支持用户显式指定 SESSION_ID，以支持不用 COOKIE 时的情况 """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        from importlib import import_module
        self.get_response = get_response
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore

    def process_request(self, request):
        # print('\n'.join(sorted(request.META.keys())))
        # session_id = request.META.get('HTTP_X_SESSIONID')
        # 实际的请求头到了 request.META 里面会变成 HTTP_ 前缀加上横杠变成下划线的转换
        session_id = request.META.get(
            ('HTTP_' + settings.CUSTOM_SESSION_HEADER).replace('-', '_')
        )
        # print(request.META.get('HTTP_X_CSRFTOKEN'))
        if session_id and self.SessionStore(session_id):
            request.COOKIES[settings.SESSION_COOKIE_NAME] = session_id

    def process_response(self, request, response):
        if request.session:
            session_id = getattr(request.session, 'session_key') or \
                         getattr(request.session, '_SessionBase__session_key')
            if session_id:
                response[settings.CUSTOM_SESSION_HEADER] = session_id
        return response


class MethodOverrideMiddleware(MiddlewareMixin):
    """
    用于支持客户端 PATCH 方法受限时，采取 POST 方法，但是添加一个 Header 来实现 PATCH 提交的功能
    Clone from https://pypi.org/project/django-method-override/
    To solve android volley request patch method no supported issue:
    https://stackoverflow.com/a/20221780/2544762
    """

    def process_request(self, request):
        if request.method != 'POST':
            return
        method = self._get_method_override(request)
        if method in settings.METHOD_OVERRIDE_ALLOWED_HTTP_METHODS:
            setattr(request, method, request.POST.copy())
            request.method = method

    def _get_method_override(self, request):
        method = (request.POST.get(settings.METHOD_OVERRIDE_PARAM_KEY) or
                  request.META.get(settings.METHOD_OVERRIDE_HTTP_HEADER))
        return method and method.upper()
