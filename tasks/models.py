from django.db import models

# Create your models here.


cmd_list = ['shell','raw','cron','file','service','user','ping','yum','setup','script','synchronize','get_url']


class tools_script(models.Model):
    TOOL_RUN_TYPE = (
        ('shell', 'shell'),
        ('python', 'python'),
        ( 'yml', 'yml'),
    )

    name = models.CharField(max_length=255, verbose_name='工具名称',unique=True)
    tool_script = models.TextField(verbose_name='脚本',null=True, blank=True)
    tool_run_type =  models.CharField(choices=TOOL_RUN_TYPE, verbose_name='脚本类型',max_length=24)
    comment = models.TextField(verbose_name='工具说明', null=True, blank=True)


    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    utime = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "tools_script"
        verbose_name = "工具"
        verbose_name_plural = verbose_name




class  tool_results(models.Model):
    task_id =  models.UUIDField(max_length=255, verbose_name='任务ID',unique=True)
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')



    # def __str__(self):
    #     return self.ctime

    class Meta:
        db_table = "tool_results"
        verbose_name = "任务"
        verbose_name_plural = verbose_name