from django.urls import path
from name import views


urlpatterns = [
    path('name.html', views.NameListAll.as_view(), name='name_list'),
    path('name-add.html', views.NameAdd.as_view(), name='name_add'),
    path('name-all-del.html', views.NameAllDel.as_view(), name='name_all_del'),
    path('name-update-<int:pk>.html', views.NameUpdate.as_view(), name='name_update'),
]

app_name = "name"


