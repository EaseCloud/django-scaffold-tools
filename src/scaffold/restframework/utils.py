""" Utils for quick setup for your DRF project.
Usage:
------

If you are no familiar with django-rest-framework, see the below tutorials:

* https://www.django-rest-framework.org/tutorial/1-serialization/#creating-a-serializer-class
* https://www.django-rest-framework.org/tutorial/6-viewsets-and-routers/#tutorial-6-viewsets-routers

So, with this module, you don't need to generate the ModalSerializer classes and ViewSet.

Just call `auto_declare_serializers` and `auto_declare_viewsets` in your code, everything is done.

Example:

In your `serializers.py`:

```
from rest_framework import serializers
from scaffold.restframework.utils import auto_declare_serializers, extend_class

# Import your models module where Model classes were defined.
from . import models as m

# Auto declare serializer classes from models.
auto_declare_serializers(m, locals())

# Optional: Type hinting for Serializer classes generated.
MemberSerializer: serializers.Serializer


#  >>> Extending serializer classes as needed.

@extend_class(MemberSerializer)
class Extender: # Use a any class name as you like except for overriding MemberSerializer itself.
    avatar_url = serializers.ReadOnlyField(source='avatar.url')
```

In your `views.py`:

```
from scaffold.restframework.utils import auto_declare_viewsets

# Automatically generated ViewSet classes from serializers.
auto_declare_viewsets(s, locals())
```

"""
import inspect
import logging
import re
from types import ModuleType
from typing import Union, List

from django.db import models
from rest_framework import viewsets, serializers
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSet

logger = logging.getLogger(__name__)


def auto_declare_serializers(models_module, context):
    """ Automatically declares classes from serializers
    :param models_module: Passes the module to search model classes.
    :param context: Context module to export classes, should passes locals().
    """
    for model in models_module.__dict__.values():
        if not inspect.isclass(model) \
                or not issubclass(model, models.Model) \
                or model._meta.abstract:
            continue
        serializer_name = model.__name__ + 'Serializer'
        # Do not override
        if serializer_name in context:
            continue
        # Derive subclass of serializers.Serializer
        serializer = type(
            serializer_name,
            (serializers.ModelSerializer,),
            dict(
                Meta=type('Meta', (object,), dict(model=model, fields='__all__')),
            )
        )
        logger.debug(f'>>> Automatically declared <class \'{serializer.__name__}\'>')
        context[serializer.__name__] = serializer


def auto_declare_viewsets(serializers_module, context):
    """ Automatically declares classes from serializers
    :param serializers_module: Passes the module to search serializer classes.
    :param context: Context module to export classes, should passes locals().
    """
    for serializer in serializers_module.__dict__.values():
        if not inspect.isclass(serializer) \
                or not issubclass(serializer, serializers.ModelSerializer):
            continue
        model = getattr(serializer, 'Meta').model
        viewset_name = model.__name__ + 'ViewSet'
        # Do not override
        if viewset_name in context:
            continue
        # Dynamic declare the subclass
        view_set = type(
            viewset_name,
            (viewsets.ModelViewSet,),
            dict(
                queryset=model.objects.all(),
                serializer_class=serializer,
                filter_fields='__all__',
                ordering=['-pk']
            )
        )
        logger.debug(f'>>> Automatically declared <class \'{view_set.__name__}\'>')
        context[view_set.__name__] = view_set


def extend_class(klass):
    """ Dynamically extends a class with another class definition
    :param klass: The class to by modified.
    """

    def klass_decorator(cls):
        """ The inner class which was inline defined and properties should be used for injection.
        :param cls: The class to by modified.
        """
        for k, v in cls.__dict__.items():
            if k in ('__module__', '__dict__'):
                continue
            if v is None and hasattr(klass, k):
                delattr(klass, k)
            else:
                setattr(klass, k, v)

    return klass_decorator


def auto_collect_urls(modules: Union[ModuleType, List[ModuleType]]):
    """ Automatically collect ViewSet classes to urls list for `urls.py`
    :param modules: passing module(s)
    :return:
    """
    router = DefaultRouter()

    routers = []

    # Fall-backs for single-module usage
    if type(modules) == ModuleType:
        modules = [modules]

    for module in modules:
        for key, item in module.__dict__.items():
            # Catches name ends with ViewSet.
            if key.endswith('ViewSet'):
                # Replacing ViewSet from uppercase to underscored naming as Rest resource name.
                name = key.replace('ViewSet', '')
                name = re.sub(r'([A-Z])', '_\\1', name)[1:].lower()
                if name:
                    # 如果name设置成功，则添加到routers数组中
                    routers.append((name, item))

    for name, item in routers:
        # print(name, item)
        # 进行视图集路由注册 register(prefix(视图集的路由前缀),viewset(视图集),base_name(路由名称的前缀))
        router.register(name, item)

    # Return urls
    return router.urls
