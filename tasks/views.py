from django.shortcuts import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, View, CreateView, UpdateView, DetailView
from django.db.models import Q
from asset.models import AssetInfo, AssetProject
from tasks.models import cmd_list, Tools, ToolsResults, Variable
from tasks.form import ToolsForm, VarsForm
from tasks.tasks import ansbile_tools
from django_celery_results.models import TaskResult
from index.password_crypt import decrypt_p
from chain import settings
from name.models import Names
from tasks.ansible_2420.runner import AdHocRunner
from tasks.ansible_2420.inventory import BaseInventory
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json, datetime, paramiko, os, logging, random, time

logger = logging.getLogger('tasks')
from pure_pagination import PageNotAnInteger, Paginator

class TasksCmd(LoginRequiredMixin, ListView):
    """
    任务cmd 界面
    """
    template_name = 'tasks/cmd.html'
    model = AssetInfo
    context_object_name = "asset_list"
    queryset = AssetInfo.objects.all()
    ordering = ('-id',)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            "tasks_active": "active",
            "tasks_cmd_active": "active",
            "cmd_list": cmd_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        """
         资产查询功能
        """
        name = Names.objects.get(username=self.request.user)
        self.queryset = super().get_queryset()
        for i in self.queryset:
            project = AssetInfo.objects.get(hostname=i)
            project_obj = AssetProject.objects.filter(projects=project)
            hasperm = name.has_perm('cmd_assetproject', project_obj)
            if not hasperm:
                self.queryset.delete(i)

        if self.request.GET.get('project'):
            project = self.request.GET.get('project', None)
            business = self.request.GET.get('business', None)
            if business is not None:
                pro = AssetProject.objects.get(id=int(project)).projects
                self.queryset = self.queryset.filter(Q(project__projects=pro), Q(business__business=business)).order_by(
                    '-id')
            else:
                self.queryset = self.queryset.filter(Q(project__projects=project)).order_by('-id')
        return self.queryset


class TasksTail(LoginRequiredMixin, ListView):
    """
    任务 tail_log  界面
    """
    template_name = 'tasks/tail.html'
    model = AssetInfo
    context_object_name = "asset_list"
    queryset = AssetInfo.objects.all()
    ordering = ('-id',)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            "tasks_active": "active",
            "tasks_tail_active": "active",
            "cmd_list": cmd_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        """
         资产查询功能
        """
        name = Names.objects.get(username=self.request.user)
        self.queryset = super().get_queryset()
        for i in self.queryset:
            project = AssetInfo.objects.get(hostname=i)
            project_obj = AssetProject.objects.filter(projects=project)
            hasperm = name.has_perm('cmd_assetproject', project_obj)
            if not hasperm:
                self.queryset.delete(i)

        if self.request.GET.get('project'):
            project = self.request.GET.get('project', None)
            business = self.request.GET.get('business', None)
            if business is not None:
                pro = AssetProject.objects.get(id=int(project)).projects
                self.queryset = self.queryset.filter(Q(project__projects=pro), Q(business__business=business)).order_by(
                    '-id')
            else:
                self.queryset = self.queryset.filter(Q(project__projects=project)).order_by('-id')
        return self.queryset


def cmdjob(assets, tasks):
    """
    :param assets:  资产帐号密码
    :param tasks:  执行的命令 和 模块
    :return:  执行结果
    """

    inventory = BaseInventory(host_list=assets)
    hostname = []
    for i in inventory.hosts:
        hostname.append(i)
    runner = AdHocRunner(inventory)
    retsult = runner.run(tasks, "all")
    ret = None
    try:
        ok = retsult.results_raw['ok']
        failed = retsult.results_raw['failed']
        unreachable = retsult.results_raw['unreachable']
        if not ok and not failed:
            ret = unreachable
        elif not ok:
            ret = failed
        else:
            ret = ok
    except Exception as e:
        logger.error("{}".format(e))

    retsult_data = []

    for i, element in enumerate(hostname):
        std, ret_host = [], {}
        for t in range(len(tasks)):
            try:
                out = ret[element]['task{}'.format(t)]['stdout']
                err = ret[element]['task{}'.format(t)]['stderr']
                std.append("{0}{1}".format(out, err))
            except Exception as e:
                logger.error(e)
                try:
                    std.append("{0} \n".format(
                        ret[hostname[i]]['task{}'.format(t)]['msg'], t + 1))
                except Exception as e:
                    logger.error("第{0}个执行失败,此任务后面的任务未执行 {1}".format(t + 1, e))
                    std.append("第{0}个执行失败,此任务后面的任务未执行".format(t + 1))

        ret_host['hostname'] = element
        ret_host['data'] = '\n'.join(std)
        retsult_data.append(ret_host)

    return retsult_data


def taillog(request, hostname, port, username, password, private, tail):
    """
    执行 tail log 接口
    """
    channel_layer = get_channel_layer()
    user = request.user.username
    os.environ["".format(user)] = "true"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if password:
        ssh.connect(hostname=hostname, port=port, username=username, password=decrypt_p(password))
    else:
        pkey = paramiko.RSAKey.from_private_key_file("{0}".format(private))
        ssh.connect(hostname=hostname, port=port, username=username, pkey=pkey)
    cmd = "tail " + tail
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    for line in iter(stdout.readline, ""):
        if os.environ.get("".format(user)) == 'false':
            break
        result = {"status": 0, 'data': line}
        result_all = json.dumps(result)
        async_to_sync(channel_layer.group_send)(user, {"type": "user.message", 'text': result_all})


class TasksPerform(LoginRequiredMixin, View):
    """
    执行 cmd  命令
    """

    @staticmethod
    def post(request):
        name = Names.objects.get(username=request.user)
        ids = request.POST.getlist('id')
        args = request.POST.getlist('args', None)
        modules = request.POST.getlist('module', None)
        ret_data = {'data': []}
        if not ids or args == [''] or not modules:
            ret = {'hostname': None, 'data': "请选中服务器,输入要执行的命令"}
            ret_data['data'].append(ret)
            return HttpResponse(json.dumps(ret_data))

        idstring = ','.join(ids)
        asset_obj = AssetInfo.objects.extra(where=['id IN (' + idstring + ')'])

        for i in asset_obj:
            project = AssetInfo.objects.get(hostname=i).project
            project_obj = AssetProject.objects.get(projects=project)
            hasperm = name.has_perm('cmd_assetproject', project_obj)
            if not hasperm:
                return HttpResponse(status=500)

        tasks, assets = [], []
        for x in range(len(modules)):
            tasks.append(
                {"action": {"module": modules[x], "args": args[x]}, "name": 'task{}'.format(x)}, )

        for i in asset_obj:
            try:
                i.user.hostname
            except Exception as e:
                logger.error(e)
                ret = {
                    'hostname': i.hostname,
                    'data': '未关联用户,请关联后再操作  {0}'.format(e)}
                ret_data['data'].append(ret)
                return HttpResponse(json.dumps(ret_data))

            var_all = {
                'hostname': i.hostname,
                'inner_ip': i.inner_ip,
                "network_ip": i.network_ip,
                "project": i.project.projects}
            try:
                var_all.update(Variable.objects.get(assets__hostname=i).vars)
            except Exception as e:
                pass
            assets.append({
                "hostname": i.hostname,
                "ip": i.network_ip,
                "port": i.port,
                "username": i.user.username,
                "password": decrypt_p(i.user.password),
                "private_key": i.user.private_key.name,
                "vars": var_all,
            }, )
        t = cmdjob(assets, tasks)
        ret_data['data'] = t
        return HttpResponse(json.dumps(ret_data))


def taskstailperform(request):
    """
    执行 tail_log  命令
    """
    if request.method == "POST":
        ret = {'status': True, 'error': None, }
        name = Names.objects.get(username=request.user)
        ids = request.POST.get('id')
        tail = request.POST.get('tail', None)

        if not ids or not tail:
            ret['status'] = False
            ret['error'] = "请选择服务器,输入参数及日志地址."
            return HttpResponse(json.dumps(ret))

        asset_obj = AssetInfo.objects.get(id=ids)
        project_obj = AssetProject.objects.get(projects=asset_obj.project)
        hasperm = name.has_perm('cmd_assetproject', project_obj)
        if not hasperm:
            return HttpResponse(status=500)
        try:
            taillog(request, asset_obj.network_ip, asset_obj.port, asset_obj.user.username, asset_obj.user.password,
                    asset_obj.user.private_key, tail)
        except Exception as e:
            ret['status'] = False
            ret['error'] = "错误{0}".format(e)
            logger.error(e)
        return HttpResponse(json.dumps(ret))


def taskstailstopperform(request):
    """
    执行 tail_log  stop  命令
    """
    if request.method == "POST":
        ret = {'status': True, 'error': None, }
        name = request.user.username
        os.environ["".format(name)] = "false"
        return HttpResponse(json.dumps(ret))


class ToolsList(LoginRequiredMixin, ListView):
    """
    工具列表
    """
    template_name = 'tasks/tools.html'
    model = Tools
    context_object_name = "tools_list"

    def get_context_data(self, **kwargs):
        context = {
            "tasks_active": "active",
            "tools_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ToolsAdd(LoginRequiredMixin, CreateView):
    """
     工具增加
    """
    model = Tools
    form_class = ToolsForm
    template_name = 'tasks/tools-add-update.html'
    success_url = reverse_lazy('tasks:tools')

    def get_context_data(self, **kwargs):
        context = {
            "tasks_active": "active",
            "tools_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ToolsUpdate(LoginRequiredMixin, UpdateView):
    """
     工具更新
    """
    model = Tools
    form_class = ToolsForm
    template_name = 'tasks/tools-add-update.html'
    success_url = reverse_lazy('tasks:tools')

    def get_context_data(self, **kwargs):
        context = {
            "tasks_active": "active",
            "tools_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ToolsAllDel(LoginRequiredMixin, View):
    """
    工具删除
    """
    model = Tools

    @staticmethod
    def post(request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                ids = request.POST.get('nid', None)
                Tools.objects.get(id=ids).delete()
            else:
                ids = request.POST.getlist('id', None)
                idstring = ','.join(ids)
                Tools.objects.extra(
                    where=['id IN (' + idstring + ')']).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))


class ToolsExec(LoginRequiredMixin, ListView):
    """
    工具执行
    """
    template_name = 'tasks/tools-exec.html'
    model = AssetInfo
    context_object_name = "asset_list"
    queryset = AssetInfo.objects.all()
    ordering = ('-id',)

    def get_context_data(self, *, object_list=None, **kwargs):
        tools_list = Tools.objects.all()
        context = {
            "tasks_active": "active",
            "tools_exec_active": "active",
            "tools_list": tools_list
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        """
         资产查询功能
        """
        name = Names.objects.get(username=self.request.user)
        self.queryset = super().get_queryset()
        for i in self.queryset:
            project = AssetInfo.objects.get(hostname=i)
            project_obj = AssetProject.objects.filter(projects=project)
            hasperm = name.has_perm('cmd_assetproject', project_obj)
            if not hasperm:
                self.queryset.delete(i)

        if self.request.GET.get('project'):
            project = self.request.GET.get('project', None)
            business = self.request.GET.get('business', None)
            if business is not None:
                pro = AssetProject.objects.get(id=int(project)).projects
                self.queryset = self.queryset.filter(Q(project__projects=pro), Q(business__business=business)).order_by(
                    '-id')
            else:
                self.queryset = self.queryset.filter(Q(project__projects=project)).order_by('-id')
        return self.queryset

    @staticmethod
    def post(request):
        """
        执行工具
        :param request:  asset_id,tool_id,priority
        :return:  ret
        """
        ret = {'status': True, 'error': None, }
        name = Names.objects.get(username=request.user)
        try:
            asset_id = request.POST.getlist('asset_id', None)
            tool_id = request.POST.getlist('tool_id', None)
            priority = request.POST.getlist('priority', None)
            if asset_id == [] or tool_id == [] or priority == ['']:
                ret['status'] = False
                ret['error'] = '未选择主机 或 未选择脚本 或 未设置优先级'
                return HttpResponse(json.dumps(ret))

            for i in priority:
                if priority.count(i) >= 2:
                    ret['status'] = False
                    ret['error'] = '优先级设置有重复 ,请重新修改！！！'
                    return HttpResponse(json.dumps(ret))

            asset_id_tring = ','.join(asset_id)
            asset_obj = AssetInfo.objects.extra(where=['id IN (' + asset_id_tring + ')'])

            for i in asset_obj:
                project = AssetInfo.objects.get(hostname=i).project
                project_obj = AssetProject.objects.get(projects=project)
                hasperm = name.has_perm('cmd_assetproject', project_obj)
                if not hasperm:
                    return HttpResponse(status=500)

            assets = []
            for i in asset_obj:
                var_all = {
                    'hostname': i.hostname,
                    'inner_ip': i.inner_ip,
                    "network_ip": i.network_ip,
                    "project": i.project.projects
                }
                try:
                    var_all.update(Variable.objects.get(assets__hostname=i).vars)
                except Exception as e:
                    pass

                assets.append({
                    "hostname": i.hostname,
                    "ip": i.network_ip,
                    "port": i.port,
                    "username": i.user.username,
                    "password": decrypt_p(i.user.password),
                    "private_key": i.user.private_key.name,
                    "vars": var_all,
                }, )

            tool_priority_1 = dict(zip(tool_id, priority))
            tool_priority = sorted(tool_priority_1.items(), key=lambda item: item[1])

            tasks = []
            for i in tool_priority:
                tool_obj = Tools.objects.get(id=i[0])
                if tool_obj.tool_run_type == 'shell' or tool_obj.tool_run_type == 'python':
                    t = time.time()
                    file = "data/script/{0}".format(int(round(t * 1000)) + random.randint(0, 999999))
                    t1 = time.time()
                    file2 = "data/script/{0}".format(int(round(t1 * 1000)) + random.randint(10000000, 99999999))
                    with open("{}.sh".format(file), 'w+') as f:
                        f.write(tool_obj.tool_script)
                    os.system("sed  's/\r//'  {0}.sh >  {1}.sh".format(file, file2))
                    tasks.append({"action": {"module": "script", "args": '{}.sh'.format(file2), },
                                  "name": 'task{}'.format(i[1])}, )

                elif tool_obj.tool_run_type == 'yml':
                    t = time.time()
                    file = "data/script/{0}".format(int(round(t * 1000)) + random.randint(0, 999999))
                    t1 = time.time()
                    file2 = "data/script/{0}".format(int(round(t1 * 1000)) + random.randint(10000000, 99999999))
                    with open("{}.yml".format(file), 'w+') as f:
                        f.write(tool_obj.tool_script)
                    os.system("sed  's/\r//'  {0}.yml >  {1}.yml".format(file, file2))
                    tasks.append({"action": {"module": "yml", "args": '{}.yml'.format(file2), },
                                  "name": 'task{}'.format(i[1])}, )

            rets = ansbile_tools.delay(assets, tasks)
            task_obj = ToolsResults.objects.create(task_id=rets.task_id, add_user=name)
            ret['id'] = task_obj.id
            return HttpResponse(json.dumps(ret))
        except Exception as e:
            ret['status'] = False
            ret['error'] = '创建任务失败,{0}'.format(e)
            return HttpResponse(json.dumps(ret))


class ToolsResultsList(LoginRequiredMixin, ListView):
    """
    执行工具 返回信息列表
    """
    ordering = ('-ctime',)
    template_name = 'tasks/tools-results.html'
    model = ToolsResults
    queryset = ToolsResults.objects.all()


    def get_context_data(self, **kwargs):
        try:
            page = self.request.GET.get('page', 1)
        except PageNotAnInteger as e:
            page = 1
        p = Paginator(self.queryset, getattr(settings, 'DISPLAY_PER_PAGE'), request=self.request)
        list = p.page(page)
        context = {
            "tasks_active": "active",
            "tools_results_active": "active",
            "tools_results_list": list,
            'date_from': (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y-%m-%d'),
            'date_to': (datetime.datetime.now() + datetime.timedelta(days=+1)).strftime('%Y-%m-%d')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        """
         资产查询功能
        """
        name = Names.objects.get(username=self.request.user)
        self.queryset = super().get_queryset()
        keyword = self.request.GET.get('keyword', '')
        if name.is_superuser != 1:
            assets = []
            for i in ToolsResults.objects.filter(add_user=name):
                assets.append(i)
            self.queryset = assets

        if self.request.GET.get('date_from'):
            self.queryset = self.queryset.filter(
                ctime__gt=self.request.GET.get('date_from'),
                ctime__lt=self.request.GET.get('date_to')
            )
        # else:
        #     datefrom = (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y-%m-%d')
        #     dateto = (datetime.datetime.now() + datetime.timedelta(days=+1)).strftime('%Y-%m-%d')
        #     self.queryset = self.queryset.filter(
        #         ctime__gt=datefrom,
        #         ctime__lt=dateto
        #     )

        if keyword:
            self.queryset = self.queryset.filter(
                add_user__icontains=keyword,
            )
        return self.queryset


class ToolsResultsDetail(LoginRequiredMixin, DetailView):
    """
     执行工具 结果详细
    """

    model = ToolsResults
    template_name = 'tasks/tools-results-detail.html'

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        name = Names.objects.get(username=self.request.user)
        task = ToolsResults.objects.get(id=pk)
        if name.is_superuser != 1:
            if task.add_user != name:
                return HttpResponse(status=500)
        try:
            results = TaskResult.objects.get(task_id=task.task_id)
        except Exception as e:
            logger.error(e)
            results = {'result': "还未完成,请稍后再查看！！"}

        context = {
            "tasks_active": "active",
            "tools_results_active": "active",
            "task": task,
            "results": results,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class VarsList(LoginRequiredMixin, ListView):
    """
    Vars变量 列表
    """
    template_name = 'tasks/vars.html'
    model = Variable
    context_object_name = "vars_list"

    def get_context_data(self, **kwargs):
        context = {
            "tasks_active": "active",
            "vars_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class VarsAdd(LoginRequiredMixin, CreateView):
    """
     Vars变量 增加
    """
    model = Variable
    form_class = VarsForm
    template_name = 'tasks/vars-add-update.html'
    success_url = reverse_lazy('tasks:vars')

    def get_context_data(self, **kwargs):
        context = {
            "tasks_active": "active",
            "vars_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class VarsUpdate(LoginRequiredMixin, UpdateView):
    """
    Vars变量 更新
    """
    model = Variable
    form_class = VarsForm
    template_name = 'tasks/vars-add-update.html'
    success_url = reverse_lazy('tasks:vars')

    def get_context_data(self, **kwargs):
        context = {
            "tasks_active": "active",
            "vars_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class VarsAllDel(LoginRequiredMixin, View):
    """
    工具删除
    """
    model = Variable

    @staticmethod
    def post(request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                ids = request.POST.get('nid', None)
                Variable.objects.get(id=ids).delete()
            else:
                ids = request.POST.getlist('id', None)
                idstring = ','.join(ids)
                Variable.objects.extra(where=['id IN (' + idstring + ')']).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))
