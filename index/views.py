from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .form import UserPasswordForm
from django.contrib.auth.hashers import  check_password
from django.contrib.auth.models import User

from  asset.form import FileForm
from django.views.generic import FormView
from asset.models import asset
from asset.models import asset as Asset
import codecs,chardet
import csv
from io import StringIO


@login_required(login_url="/login.html")
def index(request):
    """
    首页
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
                field for field in Asset._meta.fields
                if field.name not in [
                    'date_created'
                ]
            ]
            header_ = csv_data[0]
            mapping_reverse = {field.verbose_name: field.name for field in fields}
            attr = [mapping_reverse.get(n, None) for n in header_]

            import time,datetime

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
                            v1 = time.strptime(v, '%Y/%m/%d %H:%I')
                            v =  time.strftime("%Y-%m-%d %H:%M",v1)
                        except  Exception as e :
                            print(e)
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
                            v1 = time.strptime(v, '%Y/%m/%d %H:%I')
                            v =  time.strftime("%Y-%m-%d %H:%M",v1)
                        except  Exception as e :
                            print(e)
                    else:
                        continue
                    asset_dict[k] = v

                asset1 =  Asset.objects.filter(id=ids)   ##判断ID 是否存在


                if not asset1:
                    try:
                        if len(asset.objects.filter(hostname=asset_dict.get('hostname'))):
                            raise Exception(('already exists'))
                        Asset.objects.create(**asset_dict_id)
                    except Exception as e:
                        print(e)
                else:
                    for k, v in asset_dict.items():
                        if v:
                            setattr(asset, k, v)
                    try:
                        asset.objects.filter(id=ids).update(**asset_dict)
                    except Exception as e:
                        print(e)

    return render(request, 'index/index.html', {'form':form})


def login_view(request):
    """
    登录
    :param request: username,password
    :return:
    """
    error_msg = "请登录"
    error_msg1 = "用户名或密码错误,或者被禁用,请重试"

    if request.method == "GET":
        return render(request, 'index/login.html', {'error_msg': error_msg, })

    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")
        user = authenticate(request,username=u, password=p)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['is_login'] = True
                # login_ip = request.META['REMOTE_ADDR']
                # login_log.objects.create(user=request.user, ip=login_ip)
                return redirect('/index.html')
            else:
                return render(request, 'index/login.html', {'error_msg': error_msg1, })
        else:
            return render(request, 'index/login.html', {'error_msg': error_msg1, })


def logout(requset):
    """
    退出
    :param requset:
    :return:
    """
    requset.session.clear()
    return redirect('/login.html')


@login_required(login_url="/login.html")
def password_update(request):
    """
    用户密码更新
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = UserPasswordForm(request.POST)
        if form.is_valid():
            old = User.objects.get(username=request.user)
            old_pass=old.password
            input_pass =form.cleaned_data['old_password']
            check = check_password(input_pass,old_pass)
            if  check  is True:
                if  form.cleaned_data['new_password']  == form.cleaned_data['confirm_password'] :
                    password=form.cleaned_data['new_password']
                    old.set_password(password)
                    old.save()
                    msg= "修改成功"
                    return render(request, 'index/password.html', {'form': form, "msg": msg})
                else:
                    msg="两次输入的密码不一致"
                form = UserPasswordForm()
                return render(request, 'index/password.html',{'form': form, "msg": msg})
            else:
                form = UserPasswordForm()
                return render(request, 'index/password.html',{'form': form, "msg": "旧密码不对,请重新输入"})

    else:
        form = UserPasswordForm()
    return render(request, 'index/password.html',{'form': form, })