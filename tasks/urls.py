from django.urls  import path

from  tasks  import views

urlpatterns = [
    path('cmd.html', views.TasksCmd.as_view(), name='cmd'),
    path('perform.html', views.TasksPerform.as_view(), name='perform'),


    path('tools.html', views.ToolsList.as_view(), name='tools'),
    path('tools-add.html', views.ToolsAdd.as_view(), name='tools_add'),
    path('tools-bulk-del.html', views.ToolsAllDel.as_view(), name='tools_bulk_delte'),
    path('tools-update-<int:pk>.html', views.ToolsUpdate.as_view(), name='tools_update'),
    path('tools-exec.html', views.ToolsExec.as_view(), name='tools_exec'),

]

app_name="tasks"