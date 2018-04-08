from django.contrib import admin

# Register your models here.
from djcelery.models import TaskMeta,TaskSetMeta


class TaskMetaAdmin(admin.ModelAdmin):
    readonly_fields = ('result',)
admin.site.register(TaskMeta,TaskMetaAdmin)
admin.site.register(TaskSetMeta)