from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, View, CreateView, UpdateView, DetailView
from django.db.models import Q
from  asset.models import asset
from  tasks.models import cmd_list, tools_script, tool_results
from  tasks.form import ToolsForm
from djcelery.models import TaskMeta
from .tasks import ansbile_tools
from  chain import settings
from index.password_crypt import decrypt_p
from .ansible_2420.runner import AdHocRunner
from .ansible_2420.inventory import BaseInventory

import os, json, threading, logging, random

logger = logging.getLogger('tasks')


class TasksCmd(LoginRequiredMixin, ListView):
    """
    任务cmd 界面
    """
    template_name = 'tasks/cmd.html'
    model = asset
    context_object_name = "asset_list"
    queryset = asset.objects.all()
    ordering = ('id',)

    def get_queryset(self):
        self.queryset = super().get_queryset()
        if self.request.GET.get('name'):
            query = self.request.GET.get('name', None)
            queryset = self.queryset.filter(Q(project=query)).order_by('-id')
        else:
            queryset = super().get_queryset()
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):

        context = {
            "tasks_active": "active",
            "tasks_cmd_active": "active",
            "cmd_list": cmd_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class MyThread(threading.Thread):
    """
    多线程执行ansible任务
    """

    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception as e:
            logger.error(e)
            return None


def ThreadCmdJob(assets, tasks):
    """
    执行命令的线程
    :param assets:  资产帐号密码
    :param tasks:  执行的命令 和 模块
    :return:  执行结果
    """
    inventory = BaseInventory(assets)
    runner = AdHocRunner(inventory)
    retsult = runner.run(tasks, "all")
    hostname = assets[0]['hostname']

    try:
        """执行成功"""
        data = retsult.results_raw['ok'][hostname]
    except Exception as e:
        logger.error(e)
        try:
            """执行失败"""
            data = retsult.results_raw['failed'][hostname]
        except Exception as  e:
            logger.error("连接不上  {0}".format(e))
            data_fatal_msg = retsult.results_raw['unreachable'][hostname]

    task = []
    for i in range(len(tasks)):
        try:
            """任务的返回结果  成功信息 """
            tasks_std = data['task{}'.format(i)]['stdout']
            task.append(tasks_std)
        except Exception as e:
            logger.error("执行失败{0}".format(e))
            try:
                """失败信息"""
                task.append(retsult.results_raw['failed'][hostname]['task{}'.format(i)]['stderr'])
            except Exception as e:
                logger.error("执行失败{0}".format(e))
                try:
                    """连接失败"""
                    task.append("连接失败  {0}".format(data_fatal_msg['task{}'.format(i)]['msg']))
                except Exception as e:
                    logger.error('未执行任务{0}，请检查修改上面任务！！！ \n {1}'.format(e, tasks))
                    task.append('未执行任务{0},请检查修改上面任务！！！ \n \n {1}'.format(e, tasks))

    ret = {'hostname': hostname, 'data': '\n'.join(task)}
    return ret


class TasksPerform(LoginRequiredMixin, View):
    """
    执行 cmd  命令
    """

    def post(self, request):
        ids = request.POST.getlist('id')
        args = request.POST.getlist('args', None)
        module = request.POST.getlist('module', None)

        idstring = ','.join(ids)
        asset_obj = asset.objects.extra(where=['id IN (' + idstring + ')'])

        tasks, assets = [], []
        for x in range(len(module)):
            tasks.append({"action": {"module": module[x], "args": args[x]}, "name": 'task{}'.format(x)}, )

        for i in asset_obj:
            assets.append([{
                "hostname": i.hostname,
                "ip": i.network_ip,
                "port": i.port,
                "username": i.user.username,
                "password": decrypt_p(i.user.password),
                "private_key": i.user.private_key.name,
                # "vars": {'name':123}, 变量
            }], )

        t_list = []

        for i in range(asset_obj.count()):
            t = MyThread(ThreadCmdJob, args=(assets[i], tasks,))
            t_list.append(t)
            t.start()

        ret_data = {'data': []}

        for j in t_list:
            j.join()
            ret = j.get_result()
            ret_data['data'].append(ret)

        return HttpResponse(json.dumps(ret_data))


class ToolsList(LoginRequiredMixin, ListView):
    """
    工具列表
    """
    template_name = 'tasks/tools.html'
    model = tools_script
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
    model = tools_script
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
    '''
     工具更新
    '''
    model = tools_script
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
    model = tools_script

    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                id = request.POST.get('nid', None)
                tools_script.objects.get(id=id).delete()
            else:
                ids = request.POST.getlist('id', None)
                idstring = ','.join(ids)
                tools_script.objects.extra(where=['id IN (' + idstring + ')']).delete()
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
    model = asset
    context_object_name = "asset_list"
    queryset = asset.objects.all()
    ordering = ('-id',)

    def get_queryset(self):
        self.queryset = super().get_queryset()
        if self.request.GET.get('name'):
            query = self.request.GET.get('name', None)
            queryset = self.queryset.filter(Q(project=query)).order_by('-id')
        else:
            queryset = super().get_queryset()
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        tools_list = tools_script.objects.all()
        context = {
            "tasks_active": "active",
            "tools_exec_active": "active",
            "tools_list": tools_list
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


    def post(self, request):
        """
        执行工具
        :param request:  asset_id,tool_id
        :return:  ret
        """
        ret = {'status': True, 'error': None, }

        try:
            asset_id = request.POST.getlist('asset[]', None)
            tool_id = request.POST.getlist('tool[]', None)

            if asset_id == [] or tool_id == []:
                ret['status'] = False
                ret['error'] = '未选择主机 或 未选择工具'
                return HttpResponse(json.dumps(ret))

            asset_id_tring = ','.join(asset_id)

            asset_obj = asset.objects.extra(where=['id IN (' + asset_id_tring + ')'])
            tool_obj = tools_script.objects.filter(id=int(tool_id[0])).first()

            assets = []

            for i in asset_obj:
                assets.append([{
                    "hostname": i.hostname,
                    "ip": i.network_ip,
                    "port": i.port,
                    "username": i.user.username,
                    "password": decrypt_p(i.user.password),
                    "private_key": i.user.private_key.name,
                    # "vars": {'name':123}, 变量
                }], )

            file = "data/script/{0}".format(random.randint(0, 999999))
            file2 = "data/script/{0}".format(random.randint(1000000, 9999999))

            if tool_obj.tool_run_type == 'shell'  or   tool_obj.tool_run_type == 'python':

                with  open("{}.sh".format(file), 'w+') as f:
                    f.write(tool_obj.tool_script)
                os.system("sed  's/\r//'  {0}.sh >  {1}.sh".format(file, file2))
                rets = ansbile_tools.delay(assets, '{}.sh'.format(file2), "script")
            elif tool_obj.tool_run_type == 'yml':

                with  open("{}.yml".format(file), 'w+') as f:
                    f.write(tool_obj.tool_script)
                os.system("sed  's/\r//'  {0}.yml >  {1}.yml".format(file, file2))
                rets = ansbile_tools.delay(assets, '{}.yml'.format(file2), "yml")

            task_obj = tool_results.objects.create(task_id=rets.task_id)
            ret['id'] = task_obj.id

        except Exception as e:
            ret['status'] = False
            ret['error'] = '创建任务失败 {0}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))


class ToolsResultsList(LoginRequiredMixin, ListView):
    """
    执行工具 返回信息列表
    """

    ordering = ('-ctime',)
    template_name = 'tasks/tools-results.html'
    model = tool_results
    context_object_name = "tools_results_list"
    paginate_by = settings.DISPLAY_PER_PAGE

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        search_data = self.request.GET.copy()
        try:
            search_data.pop("page")
        except BaseException as  e:
            logger.error(e)

        context.update(search_data.dict())
        context = {
            "tasks_active": "active",
            "tools_results_active": "active",
            "search_data": search_data.urlencode(),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ToolsResultsDetail(LoginRequiredMixin, DetailView):
    '''
     执行工具 结果详细
    '''

    model = tool_results
    template_name = 'tasks/tools-results-detail.html'

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        task = tool_results.objects.get(id=pk)

        results = TaskMeta.objects.get(task_id=task.task_id)

        context = {
            "tasks_active": "active",
            "tools_results_active": "active",
            "task": task,
            "results": results,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
