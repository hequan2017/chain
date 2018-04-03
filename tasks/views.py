from django.shortcuts import render
from asset.models import asset
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.conf import settings
from django.db.models import Q
from  asset.models import  asset  ,asset_user
from  asset.models import  asset  as Asset
import codecs,chardet
import csv,time
from io import StringIO
import json
from django.core import serializers
from  chain import settings
from .models import cmd_list
import threading

from   .ansible_2420.runner import AdHocRunner,PlayBookRunner
from   .ansible_2420.inventory import BaseInventory

import logging
logger = logging.getLogger('tasks')



class  TasksCmd(ListView):
    template_name = 'tasks/cmd.html'
    model = asset
    context_object_name = "asset_list"
    queryset = asset.objects.all()
    ordering = ('id',)

    def get_queryset(self):
        self.queryset = super().get_queryset()
        if  self.request.GET.get('name'):
            query = self.request.GET.get('name',None)
            queryset = self.queryset.filter( Q(project=query)).order_by('-id')
        else:
            queryset = super().get_queryset()
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):

            context = {
                "tasks_active": "active",
                "tasks_cmd_active": "active",
                "cmd_list":cmd_list,
            }
            kwargs.update(context)
            return super().get_context_data(**kwargs)



class MyThread(threading.Thread):
    """
    多线程执行ansible任务
    """

    def __init__(self,func,args=()):
        super(MyThread,self).__init__()
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




def thread_cmd_job(assets,tasks):
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

    ##测试 yml文件执行
    try:
        path = "./data/test.yml"
        runers = PlayBookRunner(playbook_path=path, inventory=inventory)
        rets = runers.run()
        print(rets['results_callback'])
    except Exception as  e:
        logger.error(e)


    try:
        data = retsult.results_raw['ok'][hostname]
    except Exception as e:
        logger.error(e)
        data = retsult.results_raw['failed'][hostname]

    task = []
    for i in range(len(tasks)):
        try:
            tasks1 = data['task{}'.format(i)]['stdout']
            if tasks1 == "":
                task.append(data['task{}'.format(i)]['stderr'])
            task.append(tasks1)
        except Exception as e:
            logger.error("任务执行失败",e)
            try:
                task.append(retsult.results_raw['failed'][hostname]['task{}'.format(i)]['stderr'])
            except Exception as e:
                logger.error('未执行本任务{0}，请检查修改上面任务 \n {1}'.format(e,tasks))
                task.append('未执行本任务{0}，请检查修改上面任务 \n {1}'.format(e,tasks))
        finally:
            ret = {'hostname': hostname, 'data': '\n'.join(task)}

    return ret






class TasksPerform(View):
    """
    执行cmd  命令
    """

    def post(self,request):
            ids = request.POST.getlist('id')
            args = request.POST.getlist('args', None)
            module = request.POST.getlist('module', None)

            ids1=[]
            for i in ids:
                try:
                   ids_test = asset.objects.get(id=i).user.hostname
                   ids1.append(i)
                except Exception  as e:
                   pass

            idstring = ','.join(ids1)
            obj = asset.objects.extra(where=['id IN (' + idstring + ')'])

            tasks = []
            for x in range(len(module)):
                tasks.append({"action": {"module": module[x], "args": args[x]}, "name": 'task{}'.format(x)}, )

            ret_data = {'data': []}

            assets = []

            for i in obj:
                    assets.append([{
                            "hostname": i.hostname,
                            "ip": i.network_ip,
                            "port": i.port,
                            "username": i.user.username,
                            "password": i.user.password,
                            "private_key": i.user.private_key.name,
                            "vars":{"name": 'hequan'},
                        }],)

            t_list = []







            for i in range(obj.count()):
                    t =  MyThread(thread_cmd_job, args=(assets[i],tasks,))
                    t_list.append(t)
                    t.start()

            for j in t_list:
                    j.join()
                    ret = j.get_result()
                    ret_data['data'].append(ret)

            return HttpResponse(json.dumps(ret_data))

