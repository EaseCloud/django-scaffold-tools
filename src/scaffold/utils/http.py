from django.http import JsonResponse

import pickle

import requests
import os
import os.path
from uuid import uuid4

from django.conf import settings


class UserContext(object):
    """ 用于独立保存登录状态的 CookieJar 封装，可以持久化指定请求的 Cookie 以及部分 Header """
    SESSION_DIR = os.path.join(settings.MEDIA_ROOT, '.session')

    def __init__(self, context_id=''):
        self.context_id = context_id or str(uuid4())
        self.session_file_path = os.path.join(self.SESSION_DIR, self.context_id)
        if not os.path.isdir(os.path.dirname(self.session_file_path)):
            os.makedirs(os.path.dirname(self.session_file_path), exist_ok=True)

        if os.path.isfile(self.session_file_path):
            self.session = pickle.load(open(self.session_file_path, 'rb'))
        else:
            self.session = requests.Session()
        # 统一限定 UserAgent 免得有些站点闹别扭
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) '
                          'AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30'
        })

    def save(self):
        file = open(self.session_file_path, 'wb')
        pickle.dump(self.session, file)
        file.close()

    def delete(self):
        if os.path.isfile(self.session_file_path):
            os.remove(self.session_file_path)

    @classmethod
    def destroy(cls, context_id):
        """ 销毁一个 context_id 的缓存文件 """
        session_file = os.path.join(cls.SESSION_DIR, '.session', context_id)
        if os.path.isfile(session_file):
            os.remove(session_file)

    def print(self):
        [print('>>>>', k, '>>>>\n' + str(v), '\n<<<<\n') for k, v in self.__dict__.items()]


def response_success(msg='', *, data=None, silent=False):
    payload = dict(ok=True)
    if msg:
        payload['msg'] = msg
    if silent:
        payload['silent'] = True
    if data:
        payload['data'] = data
    return JsonResponse(payload)


def response_fail(msg='', errcode=0, *, status=400, data=None, silent=False):
    payload = dict(ok=False)
    if msg:
        payload['msg'] = msg
    if silent:
        payload['silent'] = True
    if data:
        payload['data'] = data
    if errcode:
        payload['errcode'] = errcode
    return JsonResponse(payload, status=status)
