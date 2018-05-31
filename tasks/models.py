from django.db import models
from django_celery_results.models import TaskResult
from jsonfield import JSONField
from asset.models import AssetInfo

__all__ = [
    'Tools',
    'ToolsResults',
    'Variable'
]
cmd_list = [
    'shell',
]


class Tools(models.Model):
    TOOL_RUN_TYPE = (
        ('shell', 'shell'),
        ('python', 'python'),
        ('yml', 'yml'),
    )

    name = models.CharField(max_length=255, verbose_name='工具名称', unique=True)
    tool_script = models.TextField(verbose_name='脚本', null=True, blank=True)
    tool_run_type = models.CharField(choices=TOOL_RUN_TYPE, verbose_name='脚本类型', max_length=24)
    comment = models.TextField(verbose_name='工具说明', null=True, blank=True)

    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    utime = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Tools"
        verbose_name = "工具"
        verbose_name_plural = verbose_name


class ToolsResults(models.Model):
    task_id = models.UUIDField(max_length=255, verbose_name='任务ID', unique=True)
    add_user = models.CharField(max_length=255, verbose_name='创建者', null=True, blank=True)
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    @property
    def status(self):
        status = TaskResult.objects.get(task_id=self.task_id).status
        return status

    class Meta:
        db_table = "ToolsResults"
        verbose_name = "任务"
        verbose_name_plural = verbose_name


class Variable(models.Model):
    name = models.CharField(max_length=200, verbose_name='变量组名字')
    desc = models.TextField(null=True, blank=True, verbose_name='描述')
    vars = JSONField(null=True, blank=True, default={}, verbose_name='变量')
    assets = models.ManyToManyField(AssetInfo, verbose_name='关联资产', related_name='asset', blank=True)

    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    utime = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Variable"
        verbose_name = "变量组"
        verbose_name_plural = verbose_name
