"""
Django scaffold tools - https://github.com/easecloud/django-scaffold tools

Authors: Alfred Huang (黄文超) <https://github.com/fish-ball>

2020-now @ Copyright Easecloud

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

------

Django all-in-one settings module.

Configured from 'django-admin startproject' using Django 3.0.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/

------

Environment variables:

- DJANGO_SECRET_KEY: the secret_key used by the django settings.py module.
- DJANGO_DEBUG: if you want to enable debug, set it as 1.
- DJANGO_ALLOWED_HOSTS: comma separated allowed host list. default '*'
- DJANGO_LANGUAGE: example (en-us), default zh-hans
- DJANGO_TIME_ZONE: example (UTC), default Asia/Shanghai

- DJANGO_DB_TYPE: sqlite3 / mysql(default), if more type wanted, pull-requests are welcomed.
- DJANGO_DB_HOST: default 127.0.0.1
- DJANGO_DB_PORT: default 3306
- DJANGO_DB_NAME: default django_{app_name}
    (if using sqlite3, it stands for db filename, default db.sqlite3)
- DJANGO_DB_USER: default root
- DJANGO_DB_PASS: default root
- DJANGO_DB_CHARSET: default utf8mb4
- DJANGO_DB_COLLATION: default utf8mb4_general_ci
"""

import os
import sys

from django.core.exceptions import ImproperlyConfigured

# Get the main module name
app_name = os.environ['DJANGO_SETTINGS_MODULE'].split('.')[0]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# https://stackoverflow.com/a/606574/2544762
BASE_DIR = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))

# Quick-start development base_settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'default-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG') == '1'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_REAL_IP', '127.0.0.1')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Included third-party apps
    # 'scaffold.modules',
    # 'scaffold.models.entity.media',
    'rest_framework',
    'django_cron',
    'django_filters',
]

MIDDLEWARE = [
    # 'django_base.base_utils.middleware.MethodOverrideMiddleware',
    # 'django_base.base_utils.middleware.ExplicitSessionMiddleware',
    # 生产环境建议关闭，使用手动定义的 MEDIA_URL 以及 STATIC_URL
    # 'django_base.base_utils.middleware.FullMediaUrlMiddleware',
    # 'django_base.base_utils.middleware.DebugMiddleware',
    # 'django_base.base_utils.middleware.CookieCsrfMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'scaffold.middlewares.GlobalRequestMiddleware',
    'scaffold.middlewares.CustomExceptionMiddleware',
    'scaffold.exceptions.middleware.AppErrorMiddleware',
]

ROOT_URLCONF = f'{app_name}.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = f'{app_name}.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = dict()

_db_type: str = os.environ.get('DJANGO_DB_TYPE', 'mysql').lower()
if _db_type == 'sqlite3':
    _db_name = os.environ.get('DJANGO_DB_NAME', 'db.sqlite3')
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': _db_name if _db_name.startswith('/') else os.path.join(
            BASE_DIR,
            os.environ.get('DJANGO_DB_NAME', 'db.sqlite3')
        ),
    }
elif _db_type == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DJANGO_DB_NAME', f'django_{app_name}'),
            'USER': os.environ.get('DJANGO_DB_USER', 'root'),
            'PASSWORD': os.environ.get('DJANGO_DB_USER', 'root'),
            'HOST': os.environ.get('DJANGO_DB_HOST', '127.0.0.1'),
            'PORT': os.environ.get('DJANGO_DB_PORT', '3306'),
            'OPTIONS': {
                'charset': os.environ.get('DJANGO_DB_CHARSET', 'utf8mb4'),
                'init_command': '''
                    SET default_storage_engine=MYISAM;
                    SET sql_mode='STRICT_TRANS_TABLES';
                ''',
            },
            'TEST': {
                'CHARSET': os.environ.get('DJANGO_DB_CHARSET', 'utf8mb4'),
                'COLLATION': os.environ.get('DJANGO_DB_COLLATION', 'utf8mb4_general_ci'),
            },
        },
    }
else:
    raise ImproperlyConfigured(
        f'The DJANGO_DB_TYPE \'{_db_type}\' you\'ve configured in your '
        f'environment is not supported by dajngo-scaffold-tools right now. '
        f'So please set a supported db type in (sqlite3, mysql),'
        f'or setting DATABASES settings by yourself. '
        f'If you want more DB type to be supported, a pull request is welcomed.'
    )

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = os.environ.get('DJANGO_LANGUAGE', 'zh-hans')

TIME_ZONE = os.environ.get('DJANGO_TIME_ZONE', 'Asia/Shanghai')

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

FILE_UPLOAD_PERMISSIONS = 0o644

# Django Cache
# To solve django-cron process lock issue, we switch the cache to filebased
# https://github.com/Tivix/django-cron/issues/41
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

# CORS headers
# https://pypi.org/project/django-cors-headers/

if os.environ.get('DJANGO_CORS') == '1':
    INSTALLED_APPS.insert(
        INSTALLED_APPS.index('django.contrib.staticfiles') + 1,
        'corsheaders'
    )
    MIDDLEWARE.insert(
        MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1,
        'corsheaders.middleware.CorsMiddleware',
    )

CORS_ORIGIN_ALLOW_ALL = DEBUG
CORS_ORIGIN_REGEX_WHITELIST = r'.*'
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ['null', '.local', 'localhost', '127.0.0.1']

# REST Framework
# https://www.django-rest-framework.org/

REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
    'DEFAULT_PAGINATION_CLASS':
        'scaffold.restframework.pagination.PageNumberPagination',
    # https://stackoverflow.com/a/30875830/2544762
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'scaffold.restframework.authentication.CsrfExemptSessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    # ],
    'DEFAULT_FILTER_BACKENDS': (
        # 'rest_framework.filters.SearchFilter',
        # 'rest_framework.filters.OrderingFilter',
        'django_filters.rest_framework.DjangoFilterBackend',
        'scaffold.restframework.filters.DeepFilterBackend',
        'scaffold.restframework.filters.OrderingFilter',
        'scaffold.restframework.filters.SearchFilter',
    ),
    # 'DEFAULT_RENDERER_CLASSES': (
    #     # 'rest_framework.renderers.JSONRenderer',
    #     'rest_framework.renderers.BrowsableAPIRenderer',
    # ),
    'DATE_FORMAT': '%Y-%m-%d',
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'COERCE_DECIMAL_TO_STRING': False,
    # 'EXCEPTION_HANDLER': 'core.exceptions.exception_handler',

    # Parser classes priority-wise for Swagger
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
    ],
}

# # Geo
#
# AUTO_GEO_DECODE = False
#
# # 百度地图 API_KEY
# BMAP_KEY = ''
# # 高德地图 API_KEY
# AMAP_KEY = ''
#
# # 是否将音频自动转换为 ogg/mp3
# NORMALIZE_AUDIO = True

# # ============== Payment ===============
#
# # 如果开启调试，所有实际支付的金额会变成 1 分钱
# PAYMENT_DEBUG = True

# # =============== SMS Config ===================
#
# SMS_ACCESS_KEY_ID = '----------'
# SMS_ACCESS_KEY_SECRET = '----------'
#
# SMS_SEND_INTERVAL = 60  # 短信发送时间间隔限制
# SMS_EXPIRE_INTERVAL = 1800
# SMS_SIGN_NAME = '短信签名'
# SMS_TEMPLATES = dict(
#     SIGN_IN='SMS_142655055',
#     CHANGE_PASSWORD='SMS_142655052',
#     CHANGE_MOBILE_VERIFY='SMS_142655051',
#     CHANGE_MOBILE_UPDATE='SMS_142655056',
# )
# SMS_DEBUG = False  # 不真正发送短信，将验证码直接返回
#
# # =============== JPUSH ==================
#
# JPUSH_APP_KEY = 'a286ac61a069e1bb673c122f'
# JPUSH_MASTER_SECRET = 'cf7d0e9a881dc602d23b219d'
#
# # ============== URLS ================
#
# ROOT_URLCONF = 'apps.core.urls'
# ENABLE_ADMIN_SITE = True
#
# # ============== CUSTOM SESSION HEADER ==============
# CUSTOM_SESSION_HEADER = 'SESSION-ID'
#
# # ============== MethodOverrideMiddleware =================
# METHOD_OVERRIDE_ALLOWED_HTTP_METHODS =\
# ['GET', 'HEAD', 'PUT', 'POST', 'DELETE', 'OPTIONS', 'PATCH']
# METHOD_OVERRIDE_PARAM_KEY = '_method'
# METHOD_OVERRIDE_HTTP_HEADER = 'HTTP_X_HTTP_METHOD_OVERRIDE'
#
#
API_DEBUG = False
#
# REST_DEEP_DEFAULT_DISTINCT = False
