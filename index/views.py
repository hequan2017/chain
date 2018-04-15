from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .form import UserPasswordForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

from .models import LoginLogs


@login_required(login_url="/login.html")
def index(request):
    """
    首页
    :param request:
    :return:
    """
    return render(request, 'index/index.html',)


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
        user = authenticate(request, username=u, password=p)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['is_login'] = True
                login_ip = request.META['REMOTE_ADDR']
                LoginLogs.objects.create(user=request.user, ip=login_ip)
                return redirect('/index.html')
            else:
                return render(request, 'index/login.html',
                              {'error_msg': error_msg1, })
        else:
            return render(request, 'index/login.html',
                          {'error_msg': error_msg1, })


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
            old_pass = old.password
            input_pass = form.cleaned_data['old_password']
            check = check_password(input_pass, old_pass)
            if check is True:
                if form.cleaned_data['new_password'] == form.cleaned_data['confirm_password']:
                    password = form.cleaned_data['new_password']
                    old.set_password(password)
                    old.save()
                    msg = "修改成功"
                    return render(request, 'index/password.html',
                                  {'form': form, "msg": msg})
                else:
                    msg = "两次输入的密码不一致"
                form = UserPasswordForm()
                return render(request, 'index/password.html',
                              {'form': form, "msg": msg})
            else:
                form = UserPasswordForm()
                return render(request, 'index/password.html',
                              {'form': form, "msg": "旧密码不对,请重新输入"})

    else:
        form = UserPasswordForm()
    return render(request, 'index/password.html', {'form': form, })


@login_required(login_url="/login.html")
def login_historys(request):
    """
    登录历史
    """

    obj = LoginLogs.objects.order_by('-ctime')
    return render(request,
                  'index/login-history.html',
                  {'login': obj,
                   "index_active": "active",
                   "index_login_active": "active",
                   })
