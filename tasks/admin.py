from django.contrib import admin

from .models import Tools, ToolsResults, Variable




class ToolResultsAdmin(admin.ModelAdmin):
    search_fields = ('id', 'task_id', 'add_user', 'status', 'ctime',)
    list_display = ('id', 'task_id', 'add_user', 'status', 'ctime',)
    list_display_links = ('id', 'task_id', 'add_user', 'status', 'ctime',)
    list_filter = ('id', 'ctime',)


class ToolScriptAdmin(admin.ModelAdmin):
    search_fields = ('name', 'tool_run_type', 'comment', 'ctime',)
    list_display = ('name', 'tool_run_type', 'comment', 'ctime',)
    list_display_links = ('name', 'tool_run_type', 'comment', 'ctime',)
    list_filter = ('name', 'tool_run_type', 'comment', 'ctime',)


class VarsAdmin(admin.ModelAdmin):
    search_fields = ('name', 'desc', 'assets', 'ctime',)
    list_display = ('name', 'desc', 'ctime',)
    list_display_links = ('name', 'desc', 'ctime',)
    list_filter = ('name', 'desc', 'assets', 'ctime',)


admin.site.register(ToolsResults, ToolResultsAdmin)
admin.site.register(Tools, ToolScriptAdmin)
admin.site.register(Variable, VarsAdmin)
