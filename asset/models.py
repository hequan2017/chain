from django.db import models
import random

__all__ = [
    'AssetInfo',
    'AssetLoginUser',
    'AssetProject'
]


# 登录用户
class AssetLoginUser(models.Model):
    hostname = models.CharField(max_length=64, verbose_name='名称', unique=True)
    username = models.CharField(max_length=64, verbose_name="用户名", default='root', null=True, blank=True)
    password = models.CharField(max_length=256, blank=True, null=True, verbose_name='密码')
    private_key = models.FileField(upload_to='upload/privatekey/%Y%m%d{}'.format(random.randint(0, 99999)),
                                   verbose_name="私钥", null=True, blank=True)
    project = models.ForeignKey(verbose_name='资产项目', to='AssetProject', related_name='project',
                                on_delete=models.SET_NULL, null=True)

    ps = models.CharField(max_length=10240, verbose_name="备注", null=True, blank=True)
    ctime = models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间', blank=True)
    utime = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间', blank=True)

    class Meta:
        db_table = "AssetLoginUser"
        verbose_name = "资产用户"
        verbose_name_plural = '资产用户'

    def __str__(self):
        return self.hostname


class AssetProject(models.Model):
    projects = models.CharField(max_length=128, verbose_name='资产项目')
    ps = models.CharField(max_length=1024, verbose_name="备注", null=True, blank=True)

    class Meta:
        db_table = "AssetProject"
        verbose_name = "资产项目"
        verbose_name_plural = '资产项目'
        permissions = {
            ('read_assetproject', u"只读资产项目"),
            ('cmd_assetproject', u"执行资产项目"),
        }

    def __str__(self):
        return self.projects

class AssetBusiness(models.Model):
    business = models.CharField(max_length=128, verbose_name='业务')
    ps = models.CharField(max_length=1024, verbose_name="备注", null=True, blank=True)

    class Meta:
        db_table = "AssetBusiness"
        verbose_name = "资产业务"
        verbose_name_plural = '资产业务'

    def __str__(self):
        return self.business


class AssetInfo(models.Model):
    PLATFORM_CHOICES = (
        ("阿里云", "阿里云"),
        ("AWS", "AWS"),
        ("其他", "其他")
    )
    REGION_CHOICES = (
        ("香港", '香港'),
        ("东京", '东京'),
        ("首尔", '首尔'),
        ("华北2", '华北2'),
        ("其他", '其他')
    )

    # id = models.AutoField(primary_key=True, verbose_name="id")
    hostname = models.CharField(max_length=64, verbose_name='主机名', unique=True)
    network_ip = models.GenericIPAddressField(verbose_name='外网IP', unique=True, null=True, blank=True)
    inner_ip = models.GenericIPAddressField(verbose_name='内网IP', null=True, blank=True)
    system = models.CharField(max_length=128, verbose_name='系统版本', null=True, blank=True)
    cpu = models.CharField(max_length=64, verbose_name='CPU', null=True, blank=True)
    memory = models.CharField(max_length=64, verbose_name='内存', null=True, blank=True)
    disk = models.CharField(max_length=256, verbose_name="硬盘", null=True, blank=True)
    bandwidth = models.IntegerField(verbose_name='外网带宽', null=True, blank=True, default="1")
    platform = models.CharField(max_length=128, choices=PLATFORM_CHOICES, verbose_name='平台')
    region = models.CharField(max_length=128, choices=REGION_CHOICES, verbose_name='区域')

    project = models.ForeignKey(verbose_name='资产项目', to='AssetProject', related_name='asset', on_delete=models.CASCADE,)
    business = models.ForeignKey(verbose_name='资产业务', to='AssetBusiness', related_name='asset_business',on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(verbose_name="登录用户", to='AssetLoginUser', related_name='user_name',
                             on_delete=models.SET_NULL, null=True, blank=True)

    Instance_id = models.CharField(max_length=64, verbose_name='实例ID', null=True, blank=True)

    ps = models.CharField(max_length=1024, verbose_name="备注", null=True, blank=True)
    port = models.IntegerField(verbose_name="登录端口", default='22', null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='激活')

    ctime = models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间', blank=True)
    utime = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间', blank=True)

    @property
    def users(self):
        users = AssetLoginUser.objects.get(hostname=self.user)
        return users

    class Meta:
        db_table = "AssetInfo"
        verbose_name = "资产管理"
        verbose_name_plural = '资产管理'

    def __str__(self):
        return self.hostname
