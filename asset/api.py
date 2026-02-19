from rest_framework import generics
from django.db.models import Q
from .models import AssetInfo
from .serializers import AssetSerializer
from rest_framework import permissions


class AssetList(generics.ListCreateAPIView):
    queryset = AssetInfo.objects.select_related('project', 'business', 'user').all()
    serializer_class = AssetSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        """
        支持按关键字、项目、业务和激活状态过滤，并允许排序。
        """
        queryset = super().get_queryset()
        params = self.request.query_params

        keyword = params.get('keyword', '').strip()
        if keyword:
            queryset = queryset.filter(
                Q(hostname__icontains=keyword)
                | Q(network_ip__icontains=keyword)
                | Q(inner_ip__icontains=keyword)
                | Q(project__projects__icontains=keyword)
                | Q(business__business__icontains=keyword)
            )

        project = params.get('project', '').strip()
        if project:
            queryset = queryset.filter(project__projects=project)

        business = params.get('business', '').strip()
        if business:
            queryset = queryset.filter(business__business=business)

        is_active = params.get('is_active', '').strip().lower()
        if is_active in ('true', '1', 'yes'):
            queryset = queryset.filter(is_active=True)
        elif is_active in ('false', '0', 'no'):
            queryset = queryset.filter(is_active=False)

        ordering = params.get('ordering', '-id').strip()
        allowed_ordering = {'id', '-id', 'hostname', '-hostname', 'ctime', '-ctime'}
        if ordering not in allowed_ordering:
            ordering = '-id'

        return queryset.order_by(ordering)


class AssetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssetInfo.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (permissions.AllowAny,)
