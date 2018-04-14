
from django.contrib import admin
from index.models import login_log


class LogAdmin(admin.ModelAdmin):
    search_fields = ('user', 'ip', 'ctime')
    list_display = ('user', 'ip', 'ctime')
    list_display_links = ('user', 'ip', 'ctime')
    list_filter = ('user', 'ip', 'ctime')


admin.site.register(login_log, LogAdmin)
