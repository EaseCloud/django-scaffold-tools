from rest_framework import viewsets

from . import models as m
from . import serializers as s


class ImageViewSet(viewsets.ModelViewSet):
    queryset = m.Image.objects.all()
    serializer_class = s.ImageSerializer
    filter_fields = '__all__'


class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = m.Attachment.objects.all()
    serializer_class = s.AttachmentSerializer
    filter_fields = '__all__'
    ordering = ['-pk']
