from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, View, CreateView, UpdateView, DetailView
from django.db.models import Q
from  asset.models import asset
from  tasks.models import cmd_list, tools_script, tool_results,variable
from  tasks.form import ToolsForm,VarsForm
from tasks.tasks import ansbile_tools
from djcelery.models import TaskMeta
from index.password_crypt import decrypt_p
from  chain import settings
import os, json, threading, logging, random
logger = logging.getLogger('tasks')

from tasks.ansible_2420.runner import AdHocRunner
from tasks.ansible_2420.inventory import BaseInventory

import pprint
pp = pprint.PrettyPrinter(indent=4)






class TasksCmd(LoginRequiredMixin, ListView):
    """
    任务cmd 界面
    """
    template_name = 'tasks/cmd.html'
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

        context = {
            "tasks_active": "active",
            "tasks_cmd_active": "active",
            "cmd_list": cmd_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)




def ThreadCmdJob(assets, tasks):
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

    try:
        ok = retsult.results_raw['ok']
        failed = retsult.results_raw['failed']
        unreachable = retsult.results_raw['unreachable']
        if  not ok  and  not failed  :
            ret = unreachable
        elif  not ok:
            ret = failed
        else:
            ret = ok
    except Exception as e:
        logger.error("{}".format(e))

    retsult_data = []

    for i,element in enumerate(hostname):
        std = []
        ret_host = {}
        for t  in range(len(tasks)):
            try:
                out = ret[element]['task{}'.format(t)]['stdout']
                err = ret[element]['task{}'.format(t)]['stderr']
                std.append("{0}{1}".format(out,err))
            except Exception as e:
                logger.error(e)
                try:
                    std.append("{0} \n".format(ret[hostname[i]]['task{}'.format(t)]['msg'],t+1))
                except Exception as e:
                    logger.error("第{0}个执行失败,此任务后面的任务未执行 {1}".format(t+1,e))
                    std.append("第{0}个执行失败,此任务后面的任务未执行".format(t+1))

        ret_host['hostname'] = element
        ret_host['data'] = '\n'.join(std)
        retsult_data.append(ret_host)

    return retsult_data


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

        ret_data = {'data': []}



        for i in asset_obj:

            try:
                test = i.user.hostname
            except Exception as e:
                logger.error(e)
                ret = {'hostname': i.hostname, 'data': '未关联用户,请关联后再操作  {0}'.format(e)}
                ret_data['data'].append(ret)
                return HttpResponse(json.dumps(ret_data))

            vars = {'hostname':i.hostname,'inner_ip':i.inner_ip,"network_ip":i.network_ip,"project":i.project }
            try :
                vars.update(variable.objects.get(assets__hostname=i).vars)
            except Exception as e:
                logger.error(e)

            assets.append({
                "hostname": i.hostname,
                "ip": i.network_ip,
                "port": i.port,
                "username": i.user.username,
                "password": decrypt_p(i.user.password),
                "private_key": i.user.private_key.name,
                "vars":vars ,
            }, )


        t = ThreadCmdJob(assets, tasks)
        ret_data['data']=t
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

                vars = {'hostname': i.hostname, 'inner_ip': i.inner_ip, "network_ip": i.network_ip,
                        "project": i.project}
                try:
                    vars.update(variable.objects.get(assets__hostname=i).vars)
                except Exception as e:
                    logger.error(e)

                assets.append({
                    "hostname": i.hostname,
                    "ip": i.network_ip,
                    "port": i.port,
                    "username": i.user.username,
                    "password": decrypt_p(i.user.password),
                    "private_key": i.user.private_key.name,
                    "vars": vars,
                }, )

            file = "data/script/{0}".format(random.randint(0, 999999))
            file2 = "data/script/{0}".format(random.randint(1000000, 9999999))

            if tool_obj.tool_run_type == 'shell' or tool_obj.tool_run_type == 'python':

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
            ret['error'] = '创建任务失败,{0}'.format(e)
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

        try:
            results = TaskMeta.objects.get(task_id=task.task_id)
        except Exception as e:
            results = {'result':"还未完成,请稍后再查看！！！"}
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
    Vars列表
    """
    template_name = 'tasks/vars.html'
    model = variable
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
     Vars增加
    """
    model = variable
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
    '''
     Vars更新
    '''
    model = variable
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
    model = variable

    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                id = request.POST.get('nid', None)
                variable.objects.get(id=id).delete()
            else:
                ids = request.POST.getlist('id', None)
                idstring = ','.join(ids)
                variable.objects.extra(where=['id IN (' + idstring + ')']).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))
