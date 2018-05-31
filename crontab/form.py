from django import forms
from django_celery_beat.models import  CrontabSchedule, PeriodicTask, IntervalSchedule


class CrontabScheduleForm(forms.ModelForm):
    class Meta:
        model = CrontabSchedule
        fields = '__all__'

        labels = {
            'minute': '分',
            'hour': '时',
            'day_of_week': '周',
            'day_of_month': '月',
            'month_of_year': '年',
        }





class IntervalScheduleForm(forms.ModelForm):
    class Meta:
        model = IntervalSchedule
        fields = '__all__'

        labels = {
            'every': '间隔',
            'period': '时间单位',
        }


class PeriodicTasksForm(forms.ModelForm):


    task = forms.CharField(
        label="任务名字",
        initial='tasks.tasks.ansbile_tools_crontab',
        required=True,
    )

    class Meta:
        model = PeriodicTask
        fields = ['task','name','interval','crontab','args','kwargs','enabled','expires','description']

        widgets = {
            'expires': forms.DateTimeInput(
                attrs={'type': 'date', },
            ),
        }

        labels = {
            'enabled': '开启',
            'interval': '时间间隔',
            'crontab': '定时时间',
            'args': 'args 参数',
            'kwargs': 'kwargs 参数',
            "expires":'到期时间' ,
            'description': "描述"
        }

        help_texts = {
            "name": "* 必填 任务名字",
            "args": '* 传入脚本名字 及 主机名字 ,例如: ["pwd","dev"]  多台主机 后面顺延',
            "interval":'* 时间间隔 和 定时时间 只能二选一',
            'task': '* 必填 具体任务在tasks/tasks.py 例如: tasks.tasks.ansbile_tools  [assets, tools, modules] ',
        }



