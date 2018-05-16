from django.urls import path
from name import views

urlpatterns = [
    path('name.html', views.NameListAll.as_view(), name='name_list'),
    path('name-add.html', views.NameAdd.as_view(), name='name_add'),
    path('name-all-del.html', views.NameAllDel.as_view(), name='name_all_del'),
    path('name-update-<int:pk>.html', views.NameUpdate.as_view(), name='name_update'),

    path('groups.html', views.GroupListAll.as_view(), name='groups_list'),
    path('groups-add.html', views.GroupsAdd.as_view(), name='groups_add'),
    path('groups-all-del.html', views.GroupsAllDel.as_view(), name='groups_all_del'),
    path('groups-update-<int:pk>.html', views.GroupsUpdate.as_view(), name='groups_update'),

    path('groups-object.html', views.GroupObjectListAll.as_view(), name='groups_object_list'),
    path('groups-object-add.html', views.GroupsObjectAdd.as_view(), name='groups_object_add'),
    path('groups-object-all-del.html', views.GroupsObjectAllDel.as_view(), name='groups_object_all_del'),
    path('groups-object-update-<int:pk>.html', views.GroupsObjectUpdate.as_view(), name='groups_object_update'),
]

app_name = "name"
