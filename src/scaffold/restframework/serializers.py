from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    支持动态指定字段的序列化器，传参fields，序列化和反序列化都支持
    参考：https://blog.csdn.net/hj009zzh/article/details/108850527
    """
    Meta: type

    def __init__(self, *args, **kwargs):
        """支持字段动态生成的序列化器，从默认的Meta.fields中过滤，无关字段不查不序列化"""
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allow = set(fields)
            existing = set(self.fields)
            for f in existing - allow:
                self.fields.pop(f)
