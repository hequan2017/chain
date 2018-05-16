from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from asset.models import AssetInfo,AssetProject
from index.models import LoginLogs
from name.models import Names,Groups
from index.form import UserPasswordForm


@login_required(login_url="/login.html")
def index(request):
    """
    首页
    :param request:
    :return:
    """
    assets = AssetInfo.objects.all().count()
    projects = AssetProject.objects.all().count()
    names = Names.objects.all().count()
    groups = Groups.objects.all().count()
    return render(request, 'index/index.html', {'assets_count': assets,"projects_count": projects,
                                                'names_count': names,'groups_count': groups,
                                                })


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


def logout(request):
    """
    退出
    :param request:
    :return:
    """
    request.session.clear()
    return redirect('/login.html')


class UserPasswordUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'index/password.html'
    model = Names
    form_class = UserPasswordForm
    success_url = reverse_lazy('logout')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return super().get_success_url()


@login_required(login_url="/login.html")
def login_historys(request):
    """
    登录历史
    """
    obj = LoginLogs.objects.order_by('-ctime')
    return render(request, 'index/login-history.html', {'login': obj,
                                                        "index_active": "active",
                                                        "index_login_active": "active", })


@login_required(login_url="/login.html")
def page_not_found(request):
    return render(request, 'index/404.html')


@login_required(login_url="/login.html")
def page_error(request):
    return render(request, 'index/500.html')
