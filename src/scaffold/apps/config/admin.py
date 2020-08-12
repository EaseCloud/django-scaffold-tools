from django.contrib import admin

from . import models as m

admin.register(m.Option)
admin.register(m.UserOption)
