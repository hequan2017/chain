from rest_framework import serializers
from .models import AssetInfo


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetInfo
        fields = '__all__'
