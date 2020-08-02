from django.contrib import admin

from . import models as m

# 注册所有模型
try:
    admin.site.register(m.Image)
except:
    pass
