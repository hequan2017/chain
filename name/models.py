from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from guardian.models import GroupObjectPermission

__all__ = [
    'Names',
    'Groups',
]


class Names(AbstractUser):
    ps = models.CharField(max_length=1024, verbose_name="备注", null=True, blank=True)

    class Meta:
        db_table = "Names"
        verbose_name = "系统用户管理"
        verbose_name_plural = '系统用户管理'


class Groups(Group):
    ps = models.CharField(max_length=1024, verbose_name="备注", null=True, blank=True)

    @property
    def users(self):
        users = Names.objects.get(groups=self.name)
        return users

    class Meta:
        db_table = "Groups"
        verbose_name = "系统组管理"
        verbose_name_plural = '系统组管理'
