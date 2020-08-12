from rest_framework import serializers
from ..media import serializers as media_serializer
from . import models as m


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Option
        fields = '__all__'


class VersionSerializer(serializers.ModelSerializer):
    attachment_item = media_serializer.AttachmentSerializer(source='attachment', read_only=True)

    class Meta:
        model = m.Version
        fields = '__all__'
