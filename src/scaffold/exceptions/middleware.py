from django.utils.deprecation import MiddlewareMixin

from .exceptions import AppError
from ..utils.http import response_fail


class AppErrorMiddleware(MiddlewareMixin):
    @staticmethod
    def process_exception(request, exception):
        if isinstance(exception, AppError):
            import traceback
            from sys import stderr
            from django.conf import settings
            # TODO: Collect error to message queue
            if exception.debug or settings.API_DEBUG:
                print(traceback.format_exc(), file=stderr)
            return response_fail(
                exception.messages[0],
                exception.code,
                status=exception.http_status,
                data=exception.data,
                silent=exception.silent,
            )

