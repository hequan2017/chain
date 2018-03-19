from django.urls import path
from . import views

urlpatterns = [
    path('asset.html',views.AssetListAll.as_view(),name='asset_list'),
    path('asset-add.html',views.AssetAdd.as_view(),name='asset_add'),
    path('asset-all-del.html',views.AssetAllDel.as_view(),name='asset_all_del'),
    path('asset-detail-<int:pk>.html',views.AssetDetail.as_view(),name='asset_detail'),
    path('asset-update-<int:pk>.html', views.AssetUpdate.as_view(), name='asset_update'),

    path('asset-export.html',views.AssetExport.as_view(),name='asset_export'),
    path('asset-import.html',views.AssetImport,name='asset_import'),
    path('asset-getdata.html', views.AssetGetdata, name='asset_getdata')

]

app_name="asset"