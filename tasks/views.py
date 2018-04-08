from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Q
from  asset.models import asset, asset_user
from  tasks.models import tools_script
import json
from  chain import settings
from .models import cmd_list
import threading, logging
from  tasks.form import ToolsForm
logger = logging.getLogger('tasks')
import os



from .ansible_2420.runner import AdHocRunner, PlayBookRunner
from .ansible_2420.inventory import BaseInventory




class TasksCmd(LoginRequiredMixin, ListView):
    """
    任务cmd执行
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

    # ##测试 yml文件执行
    # try:
    #     path = "./data/test.yml"
    #     runers = PlayBookRunner(playbook_path=path, inventory=inventory)
    #     rets = runers.run()
    #     print(rets['results_callback'])
    # except Exception as  e:
    #     logger.error(e)

    try:
        data = retsult.results_raw['ok'][hostname]
    except Exception as e:
        logger.error(e)
        data = retsult.results_raw['failed'][hostname]

    task = []
    for i in range(len(tasks)):
        try:
            tasks_std = data['task{}'.format(i)]['stdout']
            if tasks_std == "":
                task.append(data['task{}'.format(i)]['stderr'])
            task.append(tasks_std)
        except Exception as e:
            logger.error("任务执行失败", e)
            try:
                task.append(retsult.results_raw['failed'][hostname]['task{}'.format(i)]['stderr'])
            except Exception as e:
                logger.error('未执行任务{0}，请检查修改上面任务！！！ \n {1}'.format(e, tasks))
                task.append('未执行任务{0},请检查修改上面任务！！！ \n \n {1}'.format(e, tasks))

    ret = {'hostname': hostname, 'data': '\n'.join(task)}
    return ret


class TasksPerform(LoginRequiredMixin, View):
    """
    执行cmd  命令
    """

    def post(self, request):
        ids = request.POST.getlist('id')
        args = request.POST.getlist('args', None)
        module = request.POST.getlist('module', None)

        idstring = ','.join(ids)
        asset_obj = asset.objects.extra(where=['id IN (' + idstring + ')'])

        tasks,assets= [],[]
        for x in range(len(module)):
            tasks.append({"action": {"module": module[x], "args": args[x]}, "name": 'task{}'.format(x)}, )



        for i in asset_obj:
            assets.append([{
                "hostname": i.hostname,
                "ip": i.network_ip,
                "port": i.port,
                "username": i.user.username,
                "password": i.user.password,
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
     资产增加
    """
    model = tools_script
    form_class =  ToolsForm
    template_name = 'tasks/tools-add-update.html'
    success_url = reverse_lazy('tasks:tools')

    def get_context_data(self, **kwargs):
        context = {
            "asset_active": "active",
            "asset_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ToolsUpdate(LoginRequiredMixin, UpdateView):
    '''
     资产更新
    '''
    model = tools_script
    form_class = ToolsForm
    template_name = 'tasks/tools-add-update.html'
    success_url = reverse_lazy('tasks:tools')


    def get_context_data(self, **kwargs):
        context = {
            "asset_active": "active",
            "asset_list_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)





class ToolsAllDel(LoginRequiredMixin, View):
    """
    资产删除
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

from .tasks import ansbile_tools

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
            " tools_exec_active": "active",
            "tools_list":tools_list
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            asset_id = request.POST.getlist('asset[]', None)
            tool_id = request.POST.getlist('tool[]', None)
            asset_id_tring = ','.join(asset_id)


            print(int(tool_id[0]))
            id= int(tool_id[0])
            print(type(id))
            asset_obj = asset.objects.extra(where=['id IN (' + asset_id_tring + ')'])
            tool_obj = tools_script.objects.filter(id=id).first()

            assets = []


            for i in asset_obj:
                assets.append([{
                    "hostname": i.hostname,
                    "ip": i.network_ip,
                    "port": i.port,
                    "username": i.user.username,
                    "password": i.user.password,
                    "private_key": i.user.private_key.name,
                    # "vars": {'name':123}, 变量
                }], )

            if tool_obj.tool_run_type == 'shell':
                with  open('test.sh', 'w+') as f:
                        f.write(tool_obj.tool_script)
                        shell = '{}.sh'.format(tool_obj.id)
                os.system("sed  's/\r//'  test.sh >  {}".format(shell))
                print(assets,shell)
                for  i in assets:
                    rets = ansbile_tools.delay(i,shell)
                    print(rets)

                #
                # ret['state']=rets.state
                # ret['id']=rets.task_id

        except Exception as e:
            ret['status'] = False
            ret['error'] = '创建任务失败{0}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))