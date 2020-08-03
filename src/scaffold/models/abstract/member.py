from .meta import *


class AbstractMember(EntityModel):
    """ 会员类
    从基础的用户角色扩展，
    """

    GENDER_SECRET = ''
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_CHOICES = (
        (GENDER_SECRET, '保密'),
        (GENDER_MALE, '男'),
        (GENDER_FEMALE, '女'),
    )

    user = models.OneToOneField(
        primary_key=True,
        verbose_name='用户',
        to=User,
        related_name='%(class)s',
        db_column='user_id',
        on_delete=models.CASCADE,
    )

    nickname = models.CharField(
        verbose_name='昵称',
        max_length=255,
        blank=True,
        default='',
    )

    gender = models.CharField(
        verbose_name='性别',
        max_length=1,
        choices=GENDER_CHOICES,
        default=GENDER_SECRET,
        blank=True,
    )

    real_name = models.CharField(
        verbose_name='真实姓名',
        max_length=150,
        blank=True,
        default='',
    )

    mobile = models.CharField(
        verbose_name='手机号码',
        max_length=45,
        unique=True,
        null=True,
        blank=True,
        # base_validator=base_validator.validate_mobile,
    )

    birthday = models.DateField(
        verbose_name='生日',
        null=True,
        blank=True,
    )

    age = models.IntegerField(
        verbose_name='年龄',
        default=0,
        help_text='如果为0则根据birthday判定年龄，否则使用此数字作为年龄'
    )

    avatar = models.OneToOneField(
        verbose_name='头像',
        to='media.Image',
        related_name='%(class)s',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    search_history = models.TextField(
        verbose_name='搜索历史',
        null=True,
        blank=True,
        help_text='最近10次搜索历史，逗号分隔'
    )

    signature = models.TextField(
        verbose_name='个性签名',
        null=True,
        blank=True,
    )

    district = models.IntegerField(
        verbose_name='所在地区',
        help_text='行政区划编码，参考：https://zh.wikipedia.org/wiki/中华人民共和国行政区划',
        null=False,
        default=0,
    )

    address = models.TextField(
        verbose_name='详细地址',
        blank=True,
        default='',
    )

    session_key = models.CharField(
        verbose_name='session_key',
        max_length=255,
        blank=True,
        default='',
        help_text='用于区分单用例登录',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return '{}:{}'.format(self.mobile, self.nickname)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 将用户名和 is_active 同步到 User
        # 更换绑定手机要用到
        # self.user.username = self.mobile
        # self.user.is_active = self.is_active
        # self.user.save()

    def delete(self, *args, **kwargs):
        """ 删除的时候要连带删除 User 对象
        :param args:
        :param kwargs:
        :return:
        """
        self.user.delete()
        return super().delete(*args, **kwargs)

    # def get_age(self):
    #     import time
    #     today = time.gmtime()
    #     dy = 0
    #     if self.age:
    #         return self.age
    #     if self.birthday:
    #         birthday = self.birthday
    #         dd = today[2] - birthday.day
    #         dm = today[1] - birthday.month
    #         dy = today[0] - birthday.year
    #         if dd < 0:
    #             dd = dd + 30
    #             dm = dm - 1
    #             if dm < 0:
    #                 dm = dm + 12
    #                 dy = dy - 1
    #         if dm < 0:
    #             dm = dm + 12
    #             dy = dy - 1
    #         return dy.__str__()
    #     return None


# class MemberAddress(UserOwnedModel,
#                     EntityModel):
#     """ 会员地址，可以用于收货地址等用途
#     """
#     district = models.CharField(
#         verbose_name='地区',
#         max_length=20,
#         help_text='行政区划编号',
#     )
#
#     content = models.CharField(
#         verbose_name='详细地址',
#         max_length=255,
#     )
#
#     receiver = models.CharField(
#         verbose_name='收件人',
#         max_length=50,
#     )
#
#     mobile = models.CharField(
#         verbose_name='联系电话',
#         max_length=20,
#     )
#
#     is_default = models.BooleanField(
#         verbose_name='是否默认',
#         default=False,
#     )
#
#     class Meta:
#         verbose_name = '地址'
#         verbose_name_plural = '地址'
#         db_table = 'member_address'

class MemberPinyinMixin(models.Model):
    nickname_pinyin = models.CharField(
        verbose_name='昵称拼音',
        max_length=255,
        blank=True,
        default='',
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # 生成昵称的拼音
        from uuslug import slugify
        self.nickname_pinyin = slugify(self.nickname)
        super().save(*args, **kwargs)


class MemberConstellationMixin(models.Model):
    CONSTELLATION_ARIES = 'ARIES'
    CONSTELLATION_TAURUS = 'TAURUS'
    CONSTELLATION_GEMINI = 'GEMINI'
    CONSTELLATION_CANCER = 'CANCER'
    CONSTELLATION_LEO = 'LEO'
    CONSTELLATION_VIRGO = 'VIRGO'
    CONSTELLATION_LIBRA = 'LIBRA'
    CONSTELLATION_SCORPIO = 'SCORPIO'
    CONSTELLATION_SAGITTARIUS = 'SAGITTARIUS'
    CONSTELLATION_CAPRICORN = 'CAPRICORN'
    CONSTELLATION_AQUARIUS = 'AQUARIUS'
    CONSTELLATION_PISCES = 'PISCES'

    CONSTELLATION_CHOICES = (
        (CONSTELLATION_ARIES, '白羊座'),
        (CONSTELLATION_TAURUS, '金牛座'),
        (CONSTELLATION_GEMINI, '双子座'),
        (CONSTELLATION_CANCER, '巨蟹座'),
        (CONSTELLATION_LEO, '狮子座'),
        (CONSTELLATION_VIRGO, '处女座'),
        (CONSTELLATION_LIBRA, '天秤座'),
        (CONSTELLATION_SCORPIO, '天蝎座'),
        (CONSTELLATION_SAGITTARIUS, '射手座'),
        (CONSTELLATION_CAPRICORN, '摩羯座'),
        (CONSTELLATION_AQUARIUS, '水瓶座'),
        (CONSTELLATION_PISCES, '双鱼座'),
    )

    constellation = models.CharField(
        verbose_name='星座',
        max_length=45,
        choices=CONSTELLATION_CHOICES,
        blank=True,
        default='',
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # 如果输入了生日日期，直接确定星座
        if not self.birthday:
            self.birthday = datetime.now()
        if self.birthday:
            date_str = self.birthday.strftime('%m%d')
            if date_str < '0120':  # 摩羯座
                self.constellation = self.CONSTELLATION_CAPRICORN
            elif date_str < '0219':  # 水瓶座
                self.constellation = self.CONSTELLATION_AQUARIUS
            elif date_str < '0321':  # 双鱼座
                self.constellation = self.CONSTELLATION_PISCES
            elif date_str < '0420':  # 白羊座
                self.constellation = self.CONSTELLATION_ARIES
            elif date_str < '0521':  # 金牛座
                self.constellation = self.CONSTELLATION_TAURUS
            elif date_str < '0622':  # 双子座
                self.constellation = self.CONSTELLATION_GEMINI
            elif date_str < '0723':  # 巨蟹座
                self.constellation = self.CONSTELLATION_CANCER
            elif date_str < '0823':  # 狮子座
                self.constellation = self.CONSTELLATION_LEO
            elif date_str < '0923':  # 处女座
                self.constellation = self.CONSTELLATION_VIRGO
            elif date_str < '1024':  # 天秤座
                self.constellation = self.CONSTELLATION_LIBRA
            elif date_str < '1123':  # 天蝎座
                self.constellation = self.CONSTELLATION_SCORPIO
            elif date_str < '1222':  # 射手座
                self.constellation = self.CONSTELLATION_SAGITTARIUS
            else:  # 摩羯座
                self.constellation = self.CONSTELLATION_CAPRICORN
        super().save(*args, **kwargs)


class AbstractOAuthEntry(NullableUserOwnedModel):
    PLATFORM_WECHAT_APP = 'WECHAT_APP'
    PLATFORM_WECHAT_BIZ = 'WECHAT_BIZ'
    PLATFORM_ALIPAY = 'ALIPAY'
    PLATFORM_QQ = 'QQ'
    PLATFORM_WEIBO = 'WEIBO'
    PLATFORM_CHOICES = (
        (PLATFORM_WECHAT_APP, '微信APP'),
        (PLATFORM_WECHAT_BIZ, '微信公众平台'),
        (PLATFORM_ALIPAY, '支付宝'),
        (PLATFORM_QQ, 'QQ'),
        (PLATFORM_WEIBO, '微博'),
    )

    platform = models.CharField(
        verbose_name='第三方平台',
        max_length=20,
        choices=PLATFORM_CHOICES,
        default='',
        blank=True,
    )

    app = models.CharField(
        verbose_name='app',
        max_length=120,
        blank=True,
        default='',
    )

    openid = models.CharField(
        verbose_name='用户OpenID',
        max_length=128,
    )

    unionid = models.CharField(
        verbose_name='Union ID',
        max_length=50,
        blank=True,
    )

    nickname = models.CharField(
        verbose_name='用户昵称',
        max_length=128,
        blank=True,
        null=True,
    )

    headimgurl = models.URLField(
        verbose_name='用户头像',
        blank=True,
        null=True,
    )

    avatar = models.ImageField(
        verbose_name='头像文件',
        upload_to='oauth/avatar/',
        blank=True,
        null=True,
    )

    params = models.TextField(
        verbose_name='params',
        blank=True,
        default=''
    )

    class Meta:
        abstract = True
        verbose_name = '第三方授权'
        verbose_name_plural = '第三方授权'
        db_table = 'member_oauth_entry'
        unique_together = [['app', 'openid']]
