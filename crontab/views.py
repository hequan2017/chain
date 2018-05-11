from django.shortcuts import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View, CreateView, UpdateView
from django.urls import reverse_lazy
from name.form import NameForm, GroupsForm, GroupsObjectForm
from name.models import Names, Groups
from guardian.models import GroupObjectPermission
from django.utils.decorators import method_decorator
from guardian.decorators import permission_required_or_404
from  crontab.form import CrontabScheduleForm, IntervalScheduleForm, PeriodicTasksForm
import json, logging
from djcelery.models import CrontabSchedule, PeriodicTask, IntervalSchedule
from  djcelery.models import TaskMeta
from chain import settings

logger = logging.getLogger('crontab')


class CrontabsListAll(LoginRequiredMixin, ListView):
    """
    定时任务时间 列表
    """

    template_name = 'crontab/crontabs.html'
    model = CrontabSchedule
    context_object_name = "crontabs_list"
    queryset = CrontabSchedule.objects.all()
    ordering = ('-id',)

    def get_context_data(self, **kwargs):
        context = {
            "crontab_crontabs_active": "active",
            "crontab_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class CrontabsAdd(LoginRequiredMixin, CreateView):
    """
    定时任务时间 增加
    """
    model = CrontabSchedule
    form_class = CrontabScheduleForm
    template_name = 'crontab/crontabs-add-update.html'
    success_url = reverse_lazy('crontabs:crontabs_list')

    def get_context_data(self, **kwargs):
        context = {
            "crontab_crontabs_active": "active",
            "crontab_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class CrontabsUpdate(LoginRequiredMixin, UpdateView):
    """
    定时任务时间 更新
    """

    model = CrontabSchedule
    form_class = CrontabScheduleForm
    template_name = 'crontab/crontabs-add-update.html'
    success_url = reverse_lazy('crontabs:crontabs_list')

    def get_context_data(self, **kwargs):
        context = {
            "crontab_crontabs_active": "active",
            "crontab_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class CrontabsAllDel(LoginRequiredMixin, View):
    """
    定时任务时间 删除
    """
    model = CrontabSchedule

    @staticmethod
    def post(request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                ids = request.POST.get('nid', None)
                CrontabSchedule.objects.get(id=ids).delete()
            else:
                ids = request.POST.getlist('id', None)
                idstring = ','.join(ids)
                CrontabSchedule.objects.extra(where=['id IN (' + idstring + ')']).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))


class IntervalsListAll(LoginRequiredMixin, ListView):
    """
    时间间隔 列表
    """

    template_name = 'crontab/intervals.html'
    model = IntervalSchedule
    context_object_name = "intervals_list"
    queryset = IntervalSchedule.objects.all()
    ordering = ('-id',)

    def get_context_data(self, **kwargs):
        context = {
            "crontab_intervals_active": "active",
            "crontab_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class IntervalsAdd(LoginRequiredMixin, CreateView):
    """
    时间间隔 增加
    """
    model = IntervalSchedule
    form_class = IntervalScheduleForm
    template_name = 'crontab/intervals-add-update.html'
    success_url = reverse_lazy('crontabs:intervals_list')

    def get_context_data(self, **kwargs):
        context = {
            "crontab_intervals_active": "active",
            "crontab_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class IntervalsUpdate(LoginRequiredMixin, UpdateView):
    """
    定时任务时间 更新
    """

    model = IntervalSchedule
    form_class = IntervalScheduleForm
    template_name = 'crontab/intervals-add-update.html'
    success_url = reverse_lazy('crontabs:intervals_list')

    def get_context_data(self, **kwargs):
        context = {
            "crontab_intervals_active": "active",
            "crontab_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class IntervalsAllDel(LoginRequiredMixin, View):
    """
    时间间隔  删除
    """
    model = IntervalSchedule

    @staticmethod
    def post(request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                ids = request.POST.get('nid', None)
                IntervalSchedule.objects.get(id=ids).delete()
            else:
                ids = request.POST.getlist('id', None)
                idstring = ','.join(ids)
                IntervalSchedule.objects.extra(where=['id IN (' + idstring + ')']).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))


class PeriodicTasksListAll(LoginRequiredMixin, ListView):
    """
    周期任务 列表
    """

    template_name = 'crontab/periodicttasks.html'
    model = PeriodicTask
    context_object_name = "periodicttasks_list"
    queryset = PeriodicTask.objects.all()
    ordering = ('-id',)

    def get_context_data(self, **kwargs):
        context = {
            "crontab_periodictasks_active": "active",
            "crontab_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class PeriodicTasksAdd(LoginRequiredMixin, CreateView):
    """
    周期任务  增加
    """
    model = PeriodicTask
    form_class = PeriodicTasksForm
    template_name = 'crontab/periodicttasks-add-update.html'
    success_url = reverse_lazy('crontabs:periodictasks_list')

    def get_context_data(self, **kwargs):
        context = {
            "crontab_periodictasks_active": "active",
            "crontab_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)



class PeriodicTasksUpdate(LoginRequiredMixin, UpdateView):
    """
    周期任务 更新
    """

    model = PeriodicTask
    form_class = PeriodicTasksForm
    template_name = 'crontab/periodicttasks-add-update.html'
    success_url = reverse_lazy('crontabs:periodictasks_list')

    def get_context_data(self, **kwargs):
        context = {
            "crontab_periodictasks_active": "active",
            "crontab_active": "active",
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class PeriodicTaskAllDel(LoginRequiredMixin, View):
    """
    周期任务  删除
    """
    model = PeriodicTask

    @staticmethod
    def post(request):
        ret = {'status': True, 'error': None, }
        try:
            if request.POST.get('nid'):
                ids = request.POST.get('nid', None)
                PeriodicTask.objects.get(id=ids).delete()
            else:
                ids = request.POST.getlist('id', None)
                idstring = ','.join(ids)
                PeriodicTask.objects.extra(where=['id IN (' + idstring + ')']).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))


class PeriodicTaskReturnList(LoginRequiredMixin, ListView):
    """
    周期任务 返回结果 列表
    """
    ordering = ('-date_done',)
    template_name = 'crontab/periodictassks-results.html'
    model = TaskMeta
    context_object_name = "periodictassks_results_list"
    paginate_by = settings.DISPLAY_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_data = self.request.GET.copy()
        try:
            search_data.pop("page")
        except BaseException as e:
           pass

        context.update(search_data.dict())
        context = {
            "crontab_active": "active",
            "crontab_periodictasks_result_active": "active",
            "search_data": search_data.urlencode(),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    # def get_queryset(self):
    #     """
    #      资产查询功能
    #     """
    #     name = Names.objects.get(username=self.request.user)
    #     self.queryset = super().get_queryset()
    #     if name.is_superuser != 1:
    #         assets = []
    #         for i in ToolsResults.objects.filter(add_user=name):
    #                 assets.append(i)
    #         queryset = assets
    #     else:
    #         queryset = super().get_queryset()
    #
    #     return queryset