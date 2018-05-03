from django.contrib import admin
from asset.models import AssetInfo, AssetLoginUser,AssetProject
from guardian.admin import GuardedModelAdmin



class AssetAdmin(GuardedModelAdmin):
    search_fields = ('hostname ','network_ip', 'inner_ip','project', 'ctime')  # 定义搜索框以哪些字段可以搜索
    list_display = ('hostname', 'network_ip','inner_ip','project','platform','region','is_active')  # 每行的显示信息
    list_display_links = ('hostname', 'network_ip', 'inner_ip')  # 设置哪些字段可以点击进入编辑界面
    list_filter = ("project",'platform', 'region')


class AssetUserAdmin(GuardedModelAdmin):
    search_fields = ('hostname', 'username',)
    list_display = ('hostname', 'username', 'private_key', 'ps')
    list_display_links = ('hostname', 'username',)
    list_filter = ('hostname', 'username',)

class AssetProjectAdmin(GuardedModelAdmin):
    pass
admin.site.register(AssetInfo,AssetAdmin)
admin.site.register(AssetProject,AssetProjectAdmin)
admin.site.register(AssetLoginUser, AssetUserAdmin)

