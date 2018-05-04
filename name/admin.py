from django.contrib import admin

# Register your models here.

from django.contrib import admin
from name.models import Names,Groups
from guardian.models import GroupObjectPermission
from django.contrib.auth.models import  Permission


admin.site.register(Names)
admin.site.register(Groups)
admin.site.register(GroupObjectPermission)
admin.site.register(Permission)