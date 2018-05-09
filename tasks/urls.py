from django.urls import path

from tasks import views

urlpatterns = [
    path('cmd.html', views.TasksCmd.as_view(), name='cmd'),
    path('perform.html', views.TasksPerform.as_view(), name='perform'),

    path('tail.html', views.TasksTail.as_view(), name='tail'),
    path('tailperform.html', views.taskstailperform, name='tail_perform'),
    path('tailperform-stop.html', views.taskstailstopperform, name='tail_perform_stop'),


    path('tools.html', views.ToolsList.as_view(), name='tools'),
    path('tools-add.html', views.ToolsAdd.as_view(), name='tools_add'),
    path('tools-bulk-del.html', views.ToolsAllDel.as_view(), name='tools_bulk_delete'),
    path('tools-update-<int:pk>.html', views.ToolsUpdate.as_view(), name='tools_update'),
    path('tools-exec.html', views.ToolsExec.as_view(), name='tools_exec'),

    path('tools-results.html', views.ToolsResultsList.as_view(), name='tools_results'),
    path('tools-results-detail-<int:pk>.html', views.ToolsResultsDetail.as_view(), name='tools_results_detail'),

    path('vars.html', views.VarsList.as_view(), name='vars'),
    path('vars-add.html', views.VarsAdd.as_view(), name='vars_add'),
    path('vars-bulk-del.html', views.VarsAllDel.as_view(), name='vars_bulk_delete'),
    path('vars-update-<int:pk>.html', views.VarsUpdate.as_view(), name='vars_update'),
]

app_name = "tasks"
