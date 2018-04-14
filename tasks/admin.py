from django.contrib import admin

# Register your models here.
from djcelery.models import TaskMeta,TaskSetMeta
from .models import tools_script,tool_results,variable


class TaskMetaAdmin(admin.ModelAdmin):
    search_fields = ('task_id','status','result','date_done',)
    list_display = ('task_id','status','result','date_done',)
    list_display_links = ('task_id','status','result','date_done',)
    list_filter = ('task_id','status','date_done',)



admin.site.register(TaskMeta,TaskMetaAdmin)
admin.site.register(TaskSetMeta)


class ToolResultsAdmin(admin.ModelAdmin):
    search_fields = ('id','task_id','status','ctime',)
    list_display = ('id','task_id','status','ctime',)
    list_display_links = ('id','task_id','status','ctime',)
    list_filter = ('id','ctime',)


class ToolScriptAdmin(admin.ModelAdmin):
    search_fields = ('name','tool_run_type','comment','ctime',)
    list_display = ('name','tool_run_type','comment','ctime',)
    list_display_links = ('name','tool_run_type','comment','ctime',)
    list_filter = ('name','tool_run_type','comment','ctime',)


class VarsAdmin(admin.ModelAdmin):
    search_fields = ('name','desc','assets','ctime',)
    list_display = ('name','desc','ctime',)
    list_display_links = ('name','desc','ctime',)
    list_filter = ('name','desc','assets','ctime',)



admin.site.register(tool_results,ToolResultsAdmin)
admin.site.register(tools_script,ToolScriptAdmin)
admin.site.register(variable,VarsAdmin)