from django.conf import settings
from django.db import models


# class Menu(HierarchicalModel, models.Model):
#     seq = models.IntegerField(
#         verbose_name='序号',
#         blank=True,
#         default=0,
#     )
#
#     project = models.CharField(
#         verbose_name='项目名称',
#         max_length=50,
#         blank=True,
#         default='',
#         help_text='如果有多个后台模块，通过这个字段区分',
#     )
#
#     groups = models.ManyToManyField(
#         verbose_name='组',
#         to=Group,
#         related_name='menus',
#     )
#
#     name = models.CharField(
#         verbose_name='菜单名称',
#         max_length=100,
#         help_text='建议与路由名称同步',
#     )
#
#     title = models.CharField(
#         verbose_name='菜单标题',
#         max_length=150,
#     )
#
#     class Meta:
#         verbose_name = '菜单'
#         verbose_name_plural = '菜单'
#         db_table = 'base_menu'
#         ordering = ['seq']
#
#     def __str__(self):
#         return '%s: %s' % (self.name, self.title)


class Option(models.Model):
    """ 全局选项
    可以通过设置的 DEFAULT_OPTIONS 来指定默认的选项值
    ```
    DEFAULT_OPTIONS: dict(
        auto_login=True,
        sound=True,
        vibration=False,
    )
    ```
    """

    key = models.CharField(
        verbose_name='选项关键字', max_length=128, unique=True)

    value = models.TextField(
        verbose_name='选项值', blank=True, default='')

    class Meta:
        verbose_name = '系统选项'
        verbose_name_plural = '系统选项'
        db_table = 'base_config_option'

    def __str__(self):
        return '{} = {}'.format(self.key, self.value)

    @classmethod
    def get(cls, key):
        """ 获取选项值
        :param key: 选项的关键字
        :return: 匹配到的选项值，如果没有此选项，返回 None
        """
        opt = cls.objects.filter(key=key).first()
        return opt and opt.value

    @classmethod
    def unset(cls, key):
        """ 删除选项值
        :param key: 选项的关键字
        :return: 没有返回值
        """
        cls.objects.filter(key=key).delete()

    @classmethod
    def set(cls, key, val):
        """ 设置选项值
        :param key: 选项的关键字
        :param val: 需要设置的目标值
        :return: 没有返回值
        """
        opt, created = cls.objects.get_or_create(key=key)
        opt.value = val
        opt.save()

    @staticmethod
    def get_all():
        return dict([(item.key, item.value) for item in Option.objects.all()])


class UserOption(models.Model):
    """ 用户选项
    类似于全局选项，但是选项配置是根据用户独立配置的
    可以通过设置的 DEFAULT_OPTIONS 来指定默认的选项值
    ```
    DEFAULT_USER_OPTIONS: dict(
        auto_login=True,
        sound=True,
        vibration=False,
    )
    ```
    """

    user = models.ForeignKey(
        verbose_name='用户',
        to='auth.User',
        related_name='options',
        on_delete=models.CASCADE,
    )

    key = models.CharField(
        verbose_name='选项名', max_length=128)

    value = models.TextField(
        verbose_name='选项值', blank=True, default='')

    class Meta:
        verbose_name = '用户选项'
        verbose_name_plural = '用户选项'
        unique_together = [('user', 'key')]
        db_table = 'base_config_user_option'

    def __str__(self):
        return '{}: {} = {}'.format(self.user, self.key, self.value)

    @staticmethod
    def get_all(user):
        return dict([(item.key, item.value) for item in user.options.all()])

    @classmethod
    def set(cls, user, key, val):
        """ 设置选项值
        :param user: 用户
        :param key: 选项的关键字
        :param val: 需要设置的目标值
        :return: 没有返回值
        """
        opt, created = cls.objects.get_or_create(key=key, user=user)
        opt.value = val
        opt.save()


class Version(models.Model):
    version = models.CharField(
        verbose_name='版本号',
        max_length=20,
    )

    alias = models.CharField(
        verbose_name='版本别名',
        max_length=100,
        blank=True,
        default='',
    )

    platform = models.CharField(
        verbose_name='平台',
        max_length=20,
        blank=True,
        default='',
    )

    date_created = models.DateTimeField(
        verbose_name='创建时间',
        auto_now_add=True,
    )

    date_updated = models.DateTimeField(
        verbose_name='更新时间',
        auto_now=True,
    )

    is_active = models.BooleanField(
        verbose_name='是否可用',
        default=True,
    )

    is_master = models.BooleanField(
        verbose_name='是否主要版本',
        default=True,
        help_text='建议实践：如果是主要版本，所有低版本的客户端必须要升级到此版本才能使用，'
                  '否则为建议版本，只作提醒，不强制升级。',
    )

    description = models.TextField(
        verbose_name='版本描述',
        blank=True,
        default='',
    )

    link = models.CharField(
        verbose_name='下载链接',
        max_length=255,
        blank=True,
        default='',
    )

    attachment = models.OneToOneField(
        verbose_name='安装包附件',
        to='media.Attachment',
        related_name='version',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = '版本'
        verbose_name_plural = '版本'
        db_table = 'base_version'
        unique_together = ''
