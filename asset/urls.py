from django.urls import path
from asset import views

urlpatterns = [
    path('asset.html',views.AssetListAll.as_view(),name='asset_list'),
    path('asset-add.html',views.AssetAdd.as_view(),name='asset_add'),
    path('asset-all-del.html',views.AssetAllDel.as_view(),name='asset_all_del'),
    path('asset-detail-<int:pk>.html',views.AssetDetail.as_view(),name='asset_detail'),
    path('asset-update-<int:pk>.html', views.AssetUpdate.as_view(), name='asset_update'),
]

app_name="asset"