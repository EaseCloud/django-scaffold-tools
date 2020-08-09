import json
import re
import random
from functools import wraps
from time import time

from django.conf import settings
from django.core.exceptions import ValidationError


def sanitize_mobile(mobile):
    """ 过滤手机号码
    如果手机号码格式符合要求，直接返回
    否则抛出 ValidationError
    :param mobile:
    :return:
    """
    mobile = mobile.strip()

    from ..utils import is_valid_mobile
    assert is_valid_mobile(mobile), '手机号码格式不正确'
    return mobile


def validate_mobile_vcode(request, action, mobile, vcode):
    """ 要求 post 中提供 Session 中产生的验证码
    :param request: 请求对象
    :param action: 验证的 action 动作（不同的 action 独享一套 vcode）
    :param mobile: POST 提交过来的手机号码
    :param vcode: POST 提交过来的验证码
    :return: 如果成功返回 True，失败返回 False
    """

    from django_base.base_utils.app_error.exceptions import AppError
    _mobile, _vcode = get_vcode_info(request, action)

    if not vcode or vcode != _vcode:
        raise AppError(50001, '验证码不正确', debug=False)

    if not mobile or mobile != _mobile:
        raise AppError(50002, '手机号码不一致', debug=False)

    # 验证成功马上擦除
    clear_vcode_info(request)

    return True


def clear_vcode_info(request, action=''):
    prefix = ('mobile_vcode_' + action).strip('_')
    for key in [prefix, prefix + '_number', prefix + '_time']:
        if key in request.session:
            del request.session[key]
    request.session.modified = True


def set_vcode_info(request, mobile, vcode, action=''):
    prefix = ('mobile_vcode_' + action).strip('_')
    request.session[prefix + '_number'] = mobile
    request.session[prefix] = vcode
    request.session[prefix + '_time'] = int(time())
    request.session.modified = True


def get_vcode_info(request, action=''):
    """ 获取 Session 中存储的 验证码信息
    :param request:
    :param action:
    :return:
    """
    prefix = ('mobile_vcode_' + action).strip('_')
    # 上次请求验证码的时间
    last_sms_request_time = int(request.session.get(prefix + '_time', 0))
    # 验证码是否到期
    if time() > last_sms_request_time + settings.SMS_EXPIRE_INTERVAL:
        return None, None
    return request.session.get(prefix + '_number'), request.session.get(prefix)


def request_mobile_vcode(request, mobile, action=''):
    """
    为传入的 request 上下文（Session）产生一个手机验证码，
    发送给指定的手机号码，并且记录在 session.vcode 中。
    :param request:
    :param mobile:
    :return:
    """
    mobile = sanitize_mobile(mobile)

    prefix = 'mobile_vcode_' + action

    # 上次请求验证码的时间
    last_sms_request_time = int(request.session.get(prefix + '_time', 0))

    # 一分钟内不允许重发
    if time() < last_sms_request_time + settings.SMS_SEND_INTERVAL:
        from django_base.base_utils.app_error.exceptions import AppError
        raise AppError(
            99999,
            '您的操作过于频繁，请在 %d 秒后再试。' % (
                    last_sms_request_time + settings.SMS_SEND_INTERVAL - time()),
            debug=False
        )

    vcode = '%06d' % (random.randint(0, 1000000))

    # 如果开启了调试选项，不真正发送短信
    if not settings.SMS_DEBUG:
        sms_send(
            mobile,
            settings.SMS_TEMPLATES.get(action),
            dict(code=vcode),
        )

    set_vcode_info(request, mobile, vcode, action)
    return vcode


def sms_send(mobile, template_code, params):
    import uuid
    mobile = sanitize_mobile(mobile)
    __business_id = uuid.uuid1()

    if type(params) != str:
        params = json.dumps(params)

    # 检验发送成功与否并返回 True，失败的话抛一个错误
    from .setup_send import send_sms
    data = send_sms(__business_id, mobile, settings.SMS_SIGN_NAME, template_code, params)
    resp = json.loads(data.decode())
    if resp.get('Message') != 'OK':
        raise ValidationError(data)
    return resp


def vcode_required(action='', error=None, vcode_field='vcode', mobile_field='mobile'):
    def func(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            vcode = request.data.get(vcode_field) or ''
            mobile = request.data.get(mobile_field) or ''
            result = validate_mobile_vcode(request, action, mobile, vcode)
            if not result:
                from django_base.base_utils.app_error.exceptions import AppError
                raise error or AppError(99999, '验证码错误', debug=False)
            return view_func(self, request, *args, **kwargs)

        return _wrapped_view

    return func
