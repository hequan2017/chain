from django.contrib import admin

# Register your models here.
from djcelery.models import TaskMeta,TaskSetMeta
from .models import tools_script,tool_results

class TaskMetaAdmin(admin.ModelAdmin):
    readonly_fields = ('result',)
admin.site.register(TaskMeta,TaskMetaAdmin)
admin.site.register(TaskSetMeta)


admin.site.register(tool_results)
admin.site.register(tools_script)