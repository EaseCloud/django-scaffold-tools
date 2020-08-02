from django.core.exceptions import ValidationError


class AppError(ValidationError):
    """ 应用错误
    可以自动映射到 HTTP 错误响应输出
    """
    data = None
    http_status = None
    silent = False
    debug = False

    def __init__(self, code, message, *, data=None, http_status=400, silent=False, debug=False):
        super().__init__(message, code)
        self.data = data
        self.http_status = http_status
        self.silent = silent
        self.debug = debug

    def set_data(self, data):
        self.data = data
        return self

    def set_silent(self, silent):
        self.silent = silent
        return self

    def set_message(self, message):
        self.message = message
        return self

    def set_debug(self, debug):
        self.debug = debug
        return self

    def set_status_code(self, status_code):
        self.http_status = status_code
        return self
