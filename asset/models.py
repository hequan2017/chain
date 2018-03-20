from django.db import models


class asset(models.Model):
    PLATFORM_1 = "阿里云"
    PLATFORM_2 = "AWS"


    PLATFORM_CHOICES = (
        (PLATFORM_1, '阿里云'),
        (PLATFORM_2, 'AWS'),
    )


    REGION_CHOICES = (
        ('1', '华北2'),
        ('2', '香港'),
        ('3', '东京'),
        ('4', '美国'),
    )

    MANAGER_CHOICES=(
        ('何全','何全'),
        ('其他','其他'),
    )
    PROJECT_CHOICES=(
        ('项目1','项目1'),
        ('项目2', '项目2'),
        ('项目3', '项目3'),
        ('其他', '其他')
    )

    hostname = models.CharField(max_length=64, verbose_name='主机名',unique=True)
    network_ip = models.GenericIPAddressField(verbose_name='外网IP', null=True,blank=True)
    inner_ip = models.GenericIPAddressField(verbose_name='内网IP', null=True, blank=True)


    system = models.CharField(max_length=128,verbose_name='系统版本',null=True,blank=True)
    cpu = models.CharField(max_length=64,verbose_name='CPU',null=True,blank=True)
    memory = models.CharField(max_length=64, verbose_name='内存', null=True,blank=True)
    disk = models.CharField(max_length=256,verbose_name="硬盘",null=True,blank=True)
    bandwidth = models.IntegerField(verbose_name='带宽', null=True,blank=True,default="1")


    platform = models.ForeignKey(max_length=128, to="platform",on_delete=models.SET_NULL,null=True, verbose_name='平台')
    region = models.ForeignKey(max_length=256,to="region",on_delete=models.SET_NULL,null=True,verbose_name="区域",)

    # platform = models.CharField(max_length=128, choices=PLATFORM_CHOICES, verbose_name='平台')
    # region = models.CharField(max_length=128, choices=REGION_CHOICES, verbose_name='区域')

    manager = models.CharField(max_length=128, choices=MANAGER_CHOICES, verbose_name='负责人')
    project = models.CharField(max_length=128, choices=PROJECT_CHOICES, verbose_name='项目')



    Instance_id = models.CharField(max_length=64, verbose_name='实例ID', null=True, blank=True)
    ctime = models.DateTimeField(verbose_name='购买时间')
    utime = models.DateTimeField(verbose_name='到期时间')
    ps = models.CharField(max_length=1024,verbose_name="备注",null=True,blank=True)
    is_active = models.BooleanField(default=True, verbose_name=('激活'))

    class  Meta:
        db_table ="asset"
        verbose_name="资产管理"
        verbose_name_plural = '资产管理'
        permissions = {
            ('read_asset',u"只读资产管理"),
        }


    def __str__(self):
        return self.hostname


#平台
class platform(models.Model):
    name = models.CharField(max_length=30)


    class  Meta:
        db_table ="platform"
        verbose_name="云平台管理"
        verbose_name_plural = '云平台管理'

    def __str__(self):
        return self.name

#区域
class region(models.Model):
    name = models.CharField(max_length=40)
    platforms = models.ForeignKey(platform,on_delete=models.SET_NULL,null=True,)

    class  Meta:
        db_table ="region"
        verbose_name="云区域管理"
        verbose_name_plural = '云区域管理'


    def __str__(self):
        return self.name