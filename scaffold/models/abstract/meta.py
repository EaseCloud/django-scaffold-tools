from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from scaffold.exceptions.exceptions import AppError


# def patch_methods(model_class):
#     def do_patch(cls):
#         for k in cls.__dict__:
#             obj = getattr(cls, k)
#             if not k.startswith('_') and callable(obj):
#                 setattr(model_class, k, obj)
#
#     return do_patch


class SortableModel(models.Model):
    """ 可排序模型
    """
    sorting = models.BigIntegerField(
        verbose_name='排序',
        default=0,
        help_text='用于系统进行排序的参数，可以给用户设定或者作为计算列存储组合权重',
        db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ['-sorting']


class StickModel(models.Model):
    """ 可置顶模型
    """
    is_sticky = models.BooleanField(
        verbose_name='是否置顶',
        default=False,
        db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ['-is_sticky']


class ActiveModel(models.Model):
    """ 可以切换可用/不可用的模型
    """
    is_active = models.BooleanField(
        verbose_name='是否可用',
        default=True,
        db_index=True,
    )

    class Meta:
        abstract = True


class DatedModel(models.Model):
    """ 记录了创建时间和修改时间的模型
    """
    date_created = models.DateTimeField(
        verbose_name='创建时间',
        auto_now_add=True,
        db_index=True,
    )

    date_updated = models.DateTimeField(
        verbose_name='修改时间',
        auto_now=True,
        db_index=True,
    )

    class Meta:
        abstract = True


class NamedModel(models.Model):
    """ 有名称的模型
    """

    name = models.CharField(
        verbose_name='名称',
        max_length=255,
        blank=True,
        default='',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name or '[{}]'.format(self.pk)


class ContentModel(models.Model):
    """ 有内容的模型
    """

    content = models.TextField(
        verbose_name='内容',
        blank=True,
        default='',
    )

    excerpt = models.CharField(
        verbose_name='摘要',
        max_length=255,
        blank=True,
        default='',
    )

    class Meta:
        abstract = True


class HierarchicalModel(models.Model):
    """ 层次模型，具备 parent 和 children 属性
    """
    parent = models.ForeignKey(
        verbose_name='上级',
        to='self',
        related_name='children',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True

    def clean(self):
        # 环路检测
        p = self.parent
        while p is not None:
            if p.pk == self.pk:
                raise ValidationError('级联结构不能出现循环引用')
            p = p.parent

    @property
    def parent_name(self):
        return self.parent and getattr(self.parent, 'name', None)


class NullableUserOwnedModel(models.Model):
    """ 由用户拥有的模型类
    包含作者字段
    """

    author = models.ForeignKey(
        verbose_name='作者',
        to='auth.User',
        related_name='%(class)ss_owned',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True


class UserOwnedModel(models.Model):
    """ 由用户拥有的模型类
    包含作者字段，要求非空
    """

    author = models.ForeignKey(
        verbose_name='作者',
        to='auth.User',
        related_name='%(class)ss_owned',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class EntityModel(NamedModel,
                  SortableModel,
                  StickModel,
                  DatedModel):
    """ 实体类模型
    """

    class Meta:
        abstract = True
        ordering = ['-date_created', '-is_sticky', '-sorting']

    def __str__(self):
        return self.name or str(self.pk)


class AbstractValidationModel(models.Model):
    """ 抽象验证类
    1. 提交一次验证的时候，必须没有非 EXPIRED 的验证信息；
    2. 提交验证之后，创建一条新的 PersonalValidationInfo 信息；
    3. 新提交的验证，状态为 PENDING，记录 date_submitted；
    4. 管理员权限可以进行审批，或者驳回，改变状态并记录 date_response；
    5. 任何阶段，用户可以取消掉现有的验证信息，变成 EXPIRED 并记录时间；
    6. 取消掉唯一一条活动的验证信息之后，可以提交新的验证信息；
    """

    STATUS_DRAFT = 'DRAFT'
    STATUS_PENDING = 'PENDING'
    STATUS_REJECTED = 'REJECTED'
    STATUS_SUCCESS = 'SUCCESS'
    STATUS_EXPIRED = 'EXPIRED'
    STATUS_CHOICES = (
        (STATUS_DRAFT, '草稿'),
        (STATUS_PENDING, '等待审批'),
        (STATUS_REJECTED, '驳回'),
        (STATUS_SUCCESS, '成功'),
        (STATUS_EXPIRED, '已失效'),
    )

    status = models.CharField(
        verbose_name='验证状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )

    date_submitted = models.DateTimeField(
        verbose_name='提交时间',
        blank=True,
        null=True,
    )

    date_response = models.DateTimeField(
        verbose_name='审批时间',
        blank=True,
        null=True,
    )

    date_expired = models.DateTimeField(
        verbose_name='失效时间',
        blank=True,
        null=True,
    )

    remark = models.CharField(
        verbose_name='审核不通过原因',
        max_length=255,
        blank=True,
        default='',
    )

    class Meta:
        abstract = True

    def approve(self, *args, **kwargs):
        if self.status not in (self.STATUS_PENDING, self.STATUS_REJECTED):
            raise AppError('ERR091', '审批对象的状态必须为等待审批或者驳回')
        self.status = self.STATUS_SUCCESS
        self.date_response = datetime.now()
        self.save()

    def reject(self, reason, *args, **kwargs):
        if self.status not in (self.STATUS_PENDING,):
            raise AppError('ERR092', '审批对象的状态必须为等待审批')
        if not reason:
            raise AppError('ERR093', '请填写驳回理由')
        self.status = self.STATUS_REJECTED
        self.date_response = datetime.now()
        self.remark = reason
        self.save()


class AbstractTransactionModel(models.Model):
    debit = models.ForeignKey(
        verbose_name='借方用户',
        to=User,
        related_name='%(class)ss_debit',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text='即余额增加的账户，默认情况用户作为账户，'
                  '如需定义其他模型作为账号，派生时覆写此字段',
    )

    credit = models.ForeignKey(
        verbose_name='贷方用户',
        to=User,
        related_name='%(class)ss_credit',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text='即余额减少的账户，默认情况用户作为账户，'
                  '如需定义其他模型作为账号，派生时覆写此字段',
    )

    amount = models.DecimalField(
        verbose_name='金额',
        max_digits=18,
        decimal_places=2,
    )

    remark = models.CharField(
        verbose_name='备注',
        blank=True,
        default='',
        max_length=255,
    )

    class Meta:
        abstract = True
