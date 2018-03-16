from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from asset.models import asset
from .form import AssetForm
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.conf import settings
from django.db.models import Q
import json




class AssetListAll(LoginRequiredMixin,ListView):
    template_name = 'asset/asset.html'
    paginate_by = settings.DISPLAY_PER_PAGE
    model = asset
    context_object_name = "asset_list"
    ordering = ('id',)

    def get_context_data(self, **kwargs):
        context = {
            "asset_active": "active",
            "asset_list_active": "active",
        }

        kwargs.update(context)
        return super(AssetListAll, self).get_context_data(**kwargs)




    # def post(self, request):
    #     query = request.POST.get("name")
    #
    #     user = User.objects.get(username=request.user)
    #     if user.is_superuser == 1:
    #         ret = asset.objects.filter(Q(network_ip=query) | Q(manage_ip=query) | Q(hostname=query) | Q(
    #             inner_ip=query) | Q(model=query) | Q(
    #             eth0=query) | Q(eth1=query) | Q(eth2=query) | Q(eth3=query) |
    #                                    Q(system=query) | Q(system_user__username=query) | Q(
    #             data_center__data_center_list=query) | Q(
    #             cabinet=query) |
    #                                    Q(position=query) | Q(sn=query)
    #                                    | Q(uplink_port=query) | Q(product_line__name=query)
    #                                    )
    #     else:
    #         product1 = Group.objects.get(user=user)
    #
    #         ret = asset.objects.filter(Q(product_line__name=product1) &  Q(network_ip=query) | Q(manage_ip=query) | Q(hostname=query) | Q( inner_ip=query) | Q(model=query) | Q(eth0=query) | Q(eth1=query) | Q(eth2=query) | Q(eth3=query) |
    #                                    Q(system=query) | Q(system_user__username=query)
    #                                    | Q(data_center__data_center_list=query) | Q(cabinet=query) | Q(position=query) | Q(sn=query)| Q(uplink_port=query))
    #
    #     return render(request, 'asset/asset.html',
    #                   {"Webssh": getattr(settings, 'Webssh_ip'),
    #                    "Webssh_port": getattr(settings, 'Webssh_port'),
    #                    "asset_active": "active",
    #                    "asset_list_active": "active", "asset_list": ret})




class AssetAdd(LoginRequiredMixin,CreateView):
    model = asset
    form_class = AssetForm
    template_name = 'asset/asset-add-update.html'
    success_url = reverse_lazy('asset:asset_list')

    def form_valid(self, form):
        return super(AssetAdd, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            "asset_active": "active",
            "asset_list_active": "active",
        }
        kwargs.update(context)
        return super(AssetAdd, self).get_context_data(**kwargs)


class AssetUpdate(LoginRequiredMixin,UpdateView):
    model = asset
    form_class = AssetForm
    template_name = 'asset/asset-add-update.html'
    success_url = reverse_lazy('asset:asset_list')


    def get_context_data(self, **kwargs):
        context = {
            "asset_active": "active",
            "asset_list_active": "active",
        }
        kwargs.update(context)
        return super(AssetUpdate, self).get_context_data(**kwargs)

    def form_invalid(self, form):
        print(form.errors)
        return super(AssetUpdate, self).form_invalid(form)




class AssetDetail(LoginRequiredMixin,DetailView):
    model = asset
    template_name = 'asset/asset-detail.html'

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        detail = asset.objects.get(id=pk)

        context = {
            "asset_active": "active",
            "asset_list_active": "active",
            "assets": detail,
            "nid": pk,
        }
        kwargs.update(context)
        return super(AssetDetail, self).get_context_data(**kwargs)



class AssetDel(LoginRequiredMixin,View):
    model = asset


    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            id = request.POST.get('nid', None)
            asset.objects.get(id=id).delete()
        except Exception as e:
            ret = {
                "static": False,
                "error": '删除请求错误,没有权限{}'.format(e)
            }
        finally:
            return HttpResponse(json.dumps(ret))




class AssetAllDel(LoginRequiredMixin,View):
    model = asset


    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            ids = request.POST.getlist('id', None)
            idstring = ','.join(ids)
            asset.objects.extra(where=['id IN (' + idstring + ')']).delete()

        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))


