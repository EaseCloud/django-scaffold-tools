from django.utils.deprecation import MiddlewareMixin

from django_base.base_utils.app_error.exceptions import AppError
from django_base.base_utils.utils import response_fail


class AppErrorMiddleware(MiddlewareMixin):
    @staticmethod
    def process_exception(request, exception):
        if type(exception) == AppError:
            import traceback
            from sys import stderr
            from django.conf import settings
            if exception.debug or settings.API_DEBUG:
                print(traceback.format_exc(), file=stderr)
            return response_fail(
                exception.message,
                exception.code,
                status=exception.http_status,
                data=exception.data,
                silent=exception.silent,
            )
