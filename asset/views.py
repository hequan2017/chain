from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .form import AssetForm
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView,FormView
from django.urls import reverse_lazy
from django.conf import settings
from django.db.models import Q
from  asset.form   import  FileForm
from  asset.models import  asset  ,platform,region
from  asset.models import  asset  as Asset
import codecs,chardet
import csv,time
from io import StringIO
import json
from django.core import serializers





class AssetListAll(LoginRequiredMixin,ListView):
    '''
    列表
    '''
    template_name = 'asset/asset.html'
    paginate_by = settings.DISPLAY_PER_PAGE
    model = asset
    context_object_name = "asset_list"
    queryset = asset.objects.all()
    ordering = ('id',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_data = self.request.GET.copy()
        try:
            search_data.pop("page")
        except BaseException as  e:
            pass

        context.update(search_data.dict())
        context = {
            "asset_active": "active",
            "asset_list_active": "active",
            "search_data":search_data.urlencode()
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


    def get_queryset(self,*args,**kwargs):
        self.queryset = super().get_queryset()
        if  self.request.GET.get('name'):
            query = self.request.GET.get('name',None)
            queryset = self.queryset.filter(Q(network_ip=query)| Q(hostname=query)  | Q(inner_ip=query)  | Q(manager=query)).order_by('id')
        else:
            queryset = super().get_queryset()
        return queryset





class AssetAdd(LoginRequiredMixin,CreateView):
    """
    增加
    """
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
    '''
    更新
    '''
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
    '''
    详细
    '''
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




class AssetAllDel(LoginRequiredMixin,View):
    """
    删除
    """
    model = asset
    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            if  request.POST.get('nid') :
                id = request.POST.get('nid', None)
                asset.objects.get(id=id).delete()
            else:
                ids = request.POST.getlist('id', None)
                idstring = ','.join(ids)
                asset.objects.extra(where=['id IN (' + idstring + ')']).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))


class AssetExport(View):
    """
    资产导出
    :param request:
    :return:
    """


    def get(self,request,):

        fields = [
            field for field in Asset._meta.fields
            if field.name not in [
                'date_created'
            ]
        ]
        filename = 'assets-all.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response.write(codecs.BOM_UTF8)
        assets = Asset.objects.all()
        writer = csv.writer(response, dialect='excel', quoting=csv.QUOTE_MINIMAL)

        header = [field.verbose_name for field in fields]
        writer.writerow(header)
        for asset_ in assets:
            data = [getattr(asset_, field.name) for field in fields]
            writer.writerow(data)
        return response

    def post(self,request):
        ids = request.POST.getlist('id', None)
        idstring = ','.join(ids)
        fields = [
            field for field in   Asset._meta.fields
            if field.name not in [
                'date_created'
            ]
        ]
        filename = 'assets.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response.write(codecs.BOM_UTF8)
        assets =  Asset.objects.extra(where=['id IN (' + idstring + ')']).all()
        writer = csv.writer(response, dialect='excel', quoting=csv.QUOTE_MINIMAL)

        header = [field.verbose_name for field in fields]
        writer.writerow(header)

        for asset_ in assets:
            data = [getattr(asset_, field.name) for field in fields]
            writer.writerow(data)
        return response


def  AssetImport(request):
    """
    资产导入
    :param request:
    :return:
    """
    form = FileForm()

    if request.method =="POST":
        form = FileForm(request.POST,request.FILES)
        if form.is_valid():
            f = form.cleaned_data['file']
            det_result = chardet.detect(f.read())
            f.seek(0)  # reset file seek index

            file_data = f.read().decode(det_result['encoding']).strip(codecs.BOM_UTF8.decode())
            csv_file = StringIO(file_data)
            reader = csv.reader(csv_file)
            csv_data = [row for row in reader]

            fields = [
                field for field in asset._meta.fields
                if field.name not in [
                    'date_created'
                ]
            ]
            header_ = csv_data[0]
            mapping_reverse = {field.verbose_name: field.name for field in fields}
            attr = [mapping_reverse.get(n, None) for n in header_]

            created, updated, failed = [], [], []
            assets = []

            for row in csv_data[1:]:
                if set(row) == {''}:
                    continue
                asset_dict = dict(zip(attr, row))
                asset_dict_id = dict(zip(attr, row))
                ids = asset_dict['id']
                id_ = asset_dict.pop('id', 0)


                for k, v in asset_dict_id.items():
                    if k == 'is_active':
                        v = True if v in ['TRUE', 1, 'true'] else False
                    elif k in ['bandwidth', 'memory', 'disk', 'cpu']:
                        try:
                            v = int(v)
                        except ValueError:
                            v = 0
                    elif  k  in   ['ctime','utime']  :
                        try:
                            v1 = time.strptime(v, '%Y/%m/%d %H:%M')
                            v =  time.strftime("%Y-%m-%d %H:%M",v1)
                        except  Exception as e :
                            print(e)
                            v = v
                    else:
                        continue
                    asset_dict_id[k] =v

                for k, v in asset_dict.items():
                    if k == 'is_active':
                        v = True if v in ['TRUE', 1, 'true'] else False
                    elif k in ['bandwidth', 'memory', 'disk','cpu']:
                        try:
                            v = int(v)
                        except ValueError:
                            v = 0
                    elif  k  in   ['ctime','utime']  :
                        try:
                            v1 = time.strptime(v, '%Y/%m/%d %H:%M')
                            v =  time.strftime("%Y-%m-%d %H:%M",v1)
                        except  Exception as e :
                            print(e)
                            v = v
                    else:
                        continue
                    asset_dict[k] = v

                asset1 =  asset.objects.filter(id=ids)   ##判断ID 是否存在


                if not asset1:
                    try:
                        if len(asset.objects.filter(hostname=asset_dict.get('hostname'))):
                            raise Exception(('already exists'))
                        asset.objects.create(**asset_dict_id)
                        created.append(asset_dict['hostname'])
                        assets.append(asset)
                    except Exception as e:
                        failed.append('%s: %s' % (asset_dict['hostname'], str(e)))

                else:
                    for k, v in asset_dict.items():
                        if v:
                            setattr(asset, k, v)
                    try:
                        asset.objects.filter(id=ids).update(**asset_dict)
                        updated.append(asset_dict['hostname'])
                    except Exception as e:
                        failed.append('%s: %s' % (asset_dict['hostname'], str(e)))

            data = {
                'created': created,
                'created_info': 'Created {}'.format(len(created)),
                'updated': updated,
                'updated_info': 'Updated {}'.format(len(updated)),
                'failed': failed,
                'failed_info': 'Failed {}'.format(len(failed)),
                'valid': True,
                'msg': 'Created: {}. Updated: {}, Error: {}'.format(
                    len(created), len(updated), len(failed))
            }


            return render(request, 'asset/asset-import.html', {'form': form, "asset_active": "active",
                                                               "asset_import_active": "active",
                                                               "msg": data })

    return render(request, 'asset/asset-import.html', {'form':form,  "asset_active": "active",
            "asset_import_active": "active", })



def AssetGetdata(request):
    """
    获取 地区与区域 的对应关系
    :param request:
    :return:
    """
    name = request.GET.get('name',None)
    platforms = platform.objects.get(name=name)
    regions = platforms.region_set.all()
    data = serializers.serialize('json', regions)
    return HttpResponse(data, content_type='application/json')



