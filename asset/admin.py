from django.contrib import admin
from   .models import asset,platform,region,asset_user



admin.site.register(asset)
admin.site.register(platform)
admin.site.register(region)
admin.site.register(asset_user)
