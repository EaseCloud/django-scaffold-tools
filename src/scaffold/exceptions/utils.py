from django_base.base_utils.app_error.exceptions import AppError


def validate_params(params, validators):
    for key, validator in validators.items():
        if key not in params:
            raise AppError(40000, '缺少参数', data=dict(key=key, params=params))
        if callable(validator):
            if not validator(params[key]):
                raise AppError(40001, '参数校验失败', data=dict(key=key, params=params))
