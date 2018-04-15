from rest_framework import generics
from .models import AssetInfo
from .serializers import AssetSerializer
from rest_framework import permissions


class AssetList(generics.ListCreateAPIView):
    queryset =AssetInfo.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (permissions.AllowAny,)


class AssetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssetInfo.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (permissions.AllowAny,)
