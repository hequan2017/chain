from django.db import models



class asset(models.Model):
    PLATFORM_CHOICES = (
        ('阿里云', '阿里云'),
        ('AWS', 'AWS'),
        ('其他', '其他'),
    )
    MANAGER_CHOICES=(
        ('何全','何全'),
        ('其他','其他'),
    )

    hostname = models.CharField(max_length=64, verbose_name='主机名',unique=True)
    network_ip = models.GenericIPAddressField(verbose_name='外网IP', null=True,blank=True)
    inner_ip = models.GenericIPAddressField(verbose_name='内网IP', null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name=('是否运行'))


    system = models.CharField(max_length=128,verbose_name='系统版本',null=True,blank=True)
    cpu = models.CharField(max_length=64,verbose_name='CPU',null=True,blank=True)
    memory = models.CharField(max_length=64, verbose_name='内存', null=True,blank=True)
    disk = models.CharField(max_length=256,verbose_name="硬盘",null=True,blank=True)
    bandwidth = models.IntegerField(verbose_name='带宽', null=True,blank=True,default="1")



    platform = models.CharField(max_length=128, choices=PLATFORM_CHOICES, verbose_name='平台', )
    Instance_id = models.CharField(max_length=64, verbose_name='实例ID', null=True, blank=True)
    region = models.CharField(max_length=256, verbose_name="地区", null=True, blank=True)
    manager = models.CharField(max_length=128, choices=MANAGER_CHOICES, verbose_name='负责人')


    ctime = models.DateTimeField(verbose_name='购买时间')
    utime = models.DateTimeField(verbose_name='到期时间')


    ps = models.CharField(max_length=1024,verbose_name="备注",null=True,blank=True)


    class  Meta:
        db_table ="asset"
        verbose_name="资产管理"
        verbose_name_plural = '资产管理'
        permissions = {
            ('read_asset',u"只读资产管理"),
        }


    def __str__(self):
        return self.hostname




