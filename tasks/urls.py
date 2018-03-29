from django.urls  import path

from  tasks  import views

urlpatterns = [
    path('cmd.html', views.TasksCmd.as_view(), name='cmd'),
    path('perform.html', views.TasksPerform.as_view(), name='perform'),

]

app_name="tasks"