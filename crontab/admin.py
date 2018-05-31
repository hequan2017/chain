
from django.contrib import admin
from django_celery_results.models import TaskResult



class TaskMetaAdmin(admin.ModelAdmin):
    search_fields = ('task_id', 'status', 'result', 'date_done',)
    list_display = ('task_id', 'status', 'result', 'date_done',)
    list_display_links = ('task_id', 'status', 'result', 'date_done',)
    list_filter = ('task_id', 'status', 'date_done',)

admin.site.register(TaskResult, TaskMetaAdmin)
