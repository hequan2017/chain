from django.urls import path
from  crontab import views

urlpatterns = [
    path('crontabs.html', views.CrontabsListAll.as_view(), name='crontabs_list'),
    path('crontabs-add.html', views.CrontabsAdd.as_view(), name='crontabs_add'),
    path('crontabs-all-del.html', views.CrontabsAllDel.as_view(), name='crontabs_all_del'),
    path('crontabs-update-<int:pk>.html', views.CrontabsUpdate.as_view(), name='crontabs_update'),

    path('intervals.html', views.IntervalsListAll.as_view(), name='intervals_list'),
    path('intervals-add.html', views.IntervalsAdd.as_view(), name='intervals_add'),
    path('intervals-all-del.html', views.IntervalsAllDel.as_view(), name='intervals_all_del'),
    path('intervals-update-<int:pk>.html', views.IntervalsUpdate.as_view(), name='intervals_update'),

    path('periodictasks.html', views.PeriodicTasksListAll.as_view(), name='periodictasks_list'),
    path('periodictasks-add.html', views.PeriodicTasksAdd.as_view(), name='periodictasks_add'),
    path('periodictasks-all-del.html', views.PeriodicTaskAllDel.as_view(), name='periodictasks_all_del'),
    path('periodictasks-update-<int:pk>.html', views.PeriodicTasksUpdate.as_view(), name='periodictasks_update'),

    path('periodictasks-results.html', views.PeriodicTaskReturnList.as_view(), name='periodictasks_result'),
]



app_name = "crontabs"


