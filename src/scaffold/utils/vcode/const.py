from django.conf import settings

ACCESS_KEY_ID = getattr(settings, 'SMS_ACCESS_KEY_ID', None)
ACCESS_KEY_SECRET = getattr(settings, 'SMS_ACCESS_KEY_SECRET', None)
