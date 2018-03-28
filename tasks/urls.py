from django.urls  import path

from  .import views

urlpatterns = [
    path('cmd.html', views.TasksCmd.as_view(), name='cmd'),
    path('perform.html', views.TasksPerform.as_view(), name='perform'),


    # path('tools.html', views.ToolsListAll.as_view(), name='tools'),
    # path('tools-add.html', views.tools_add, name='tools_add'),
    # path('tools-del.html', views.tools_delete, name='tools_delete'),
    # path('tools-bulk-del.html', views.tools_bulk_delte, name='tools_bulk_delte'),
    # path('tools-update-<int:nid>.html', views.tools_update, name='tools_update'),

]

app_name="tasks"