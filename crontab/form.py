from django import forms
from djcelery.models import CrontabSchedule, PeriodicTask, IntervalSchedule


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
    class Meta:
        model = PeriodicTask
        fields = '__all__'

        labels = {
            'task': '任务名字',
            'interval': '时间间隔',
            'crontab': '定时时间',
            'args': 'args 参数',
            'kwargs': 'kwargs 参数',
        }

        help_texts = {
            "name": "* 必填 任务名字",
            'task': '* 必填 具体任务在tasks/tasks.py 例如: tasks.tasks.test ',
        }
