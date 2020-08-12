from django.db import models

from scaffold.exceptions.exceptions import AppError


class AbstractAttachment(models.Model):
    FILE_FIELD_NAME = ''

    name = models.CharField(
        verbose_name='名称',
        max_length=255,
        blank=True,
        default='',
    )

    ext_url = models.URLField(
        verbose_name='外部附件链接',
        blank=True,
        null=False,
        default='',
    )

    class Meta:
        verbose_name = '抽象附件'
        abstract = True

    def __str__(self):
        return self.name

    def url(self):
        file_field = getattr(self, self.FILE_FIELD_NAME)
        return file_field.url if file_field else self.ext_url

    def save(self, *args, **kwargs):
        file_field = getattr(self, self.FILE_FIELD_NAME)
        if not self.name and file_field:
            self.name = file_field.name
        super().save(*args, **kwargs)


class Image(AbstractAttachment,
            models.Model):
    """ 图片
    TODO: 考虑支持七牛引擎的问题
    TODO: 还要考虑裁剪缩略图的问题
    TODO: 存放的路径要按照 md5sum 折叠，以节省空间
    """
    FILE_FIELD_NAME = 'image'

    image = models.ImageField(
        verbose_name='图片',
        upload_to='images/',
        null=False,
        blank=True,
    )

    class Meta:
        verbose_name = '图片'
        verbose_name_plural = '图片'
        db_table = 'base_media_image'

    def set_file_path(self, path):
        from django.core.files import File
        import os.path
        self.image.save(os.path.basename(path), File(open(path, 'rb')))
        self.save()

    @classmethod
    def from_file_path(cls, path):
        """ 工厂方法
        根据服务器本地文件路径构造一个对象
        :return:
        """
        from django.core.files import File
        import os.path
        obj = cls()
        obj.image.save(os.path.basename(path), File(open(path, 'rb')))
        obj.save()
        # print(obj, obj.id)
        return obj

    @classmethod
    def from_file(cls, file):
        """ TODO: 工厂方法
        根据提交的 file 构造一个对象
        如果存在相同的 md5sum
        :return:
        """

    @classmethod
    def from_url_reference(cls, url):
        """ 工厂方法
        根据指定的 url 生成一个引用的 Attachment 对象
        :return:
        """
        return cls.objects.create(ext_url=url, name=url.split('/')[-1])

    @classmethod
    def from_url_download(cls, url):
        """ TODO: 工厂方法
        根据指定的 url 下载图片保存，生成一个对象
        :return:
        """
        raise AppError(99999, '尚未实现', debug=True)


class Video(AbstractAttachment,
            models.Model):
    """ 视频对象
    """

    video = models.FileField(
        verbose_name='视频',
        upload_to='video/'
    )

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = '视频'
        db_table = 'base_media_video'


class Audio(AbstractAttachment,
            models.Model):
    """ 音频对象
    """

    audio = models.FileField(
        verbose_name='音频',
        upload_to='audio/'
    )

    is_active = models.BooleanField(
        verbose_name='是否可用',
        default=True,
    )

    class Meta:
        verbose_name = '音频'
        verbose_name_plural = '音频'
        db_table = 'base_media_audio'


class GalleryModel(models.Model):
    images = models.ManyToManyField(
        verbose_name='图片',
        to=Image,
        related_name='%(class)ss_attached',
        blank=True,
    )

    class Meta:
        abstract = True

    @property
    def images_url(self):
        return [img.url() for img in self.images.all()]


class Attachment(AbstractAttachment,
                 models.Model):
    FILE_FIELD_NAME = 'file'

    file = models.FileField(
        verbose_name='上传附件',
        upload_to='attachment/',
        null=False,
        blank=True,
    )

    class Meta:
        verbose_name = '附件'
        verbose_name_plural = '附件'
        db_table = 'base_media_attachment'
