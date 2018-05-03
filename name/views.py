from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from name.form import NameForm
from django.conf import settings
from django.db.models import Q
from name.models import Names
from asset.models import AssetInfo, AssetLoginUser,AssetProject
from asset.models import AssetInfo as Asset
from io import StringIO
from chain import settings
from index.password_crypt import encrypt_p, decrypt_p
from os import system
from tasks.models import Variable
from tasks.tasks import ansbile_asset_hardware
import csv
import json
import logging
import codecs
import chardet
import time
logger = logging.getLogger('name')



class NameListAll(LoginRequiredMixin, ListView):
    """资产列表"""
    template_name = 'name/name.html'
    paginate_by = settings.DISPLAY_PER_PAGE
    model =  Names
    context_object_name = "name_list"
    queryset = Names.objects.all()
    ordering = ('id',)


    def get_context_data(self, **kwargs):
        context = {
            "name_active": "active",
            "name_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class NameAdd(LoginRequiredMixin, CreateView):
    """
    登录用户增加
    """
    model = Names
    form_class = NameForm
    template_name = 'name/name-add-update.html'
    success_url = reverse_lazy('name:name_list')

    def get_context_data(self, **kwargs):
        context = {
            "name_active": "active",
            "name_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        forms = form.save()
        password_form = form.cleaned_data['password']
        if password_form is not None:
            forms.set_password(password_form)
            forms.save()
        return super().form_valid(form)

class NameUpdate(LoginRequiredMixin, UpdateView):
    """登录用户更新"""

    model = Names
    form_class = NameForm
    template_name = 'name/name-add-update.html'
    success_url = reverse_lazy('name:name_list')

    def get_context_data(self, **kwargs):
        context = {
            "name_active": "active",
            "name_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


    def form_valid(self, form):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        obj = Names.objects.get(id=pk)
        old_password = obj.password
        new_password = form.cleaned_data['password']

        forms = form.save()
        if new_password == "1":
            print("没修改")
            forms.password = old_password
        else:
            print("修改密码了")
            forms.set_password(new_password)
        forms.save()
        return super().form_valid(form)



class NameAllDel(LoginRequiredMixin, View):
    """
    登录用户删除
    """
    model = Names

    @staticmethod
    def post(request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                ids = request.POST.get('nid', None)
                Names.objects.get(id=ids).delete()
            else:
                ids = request.POST.getlist('id', None)
                idstring = ','.join(ids)
                Names.objects.extra(
                    where=['id IN (' + idstring + ')']).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))
