from rest_framework import serializers
from . import models as m


class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.URLField(read_only=True)

    class Meta:
        model = m.Attachment
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.URLField(read_only=True)

    class Meta:
        model = m.Image
        fields = '__all__'
