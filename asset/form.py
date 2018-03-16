from    django import forms
from .models import asset





class AssetForm(forms.ModelForm):
    class Meta:
        model = asset
        fields = '__all__'

        labels={
            "network_ip":"外网IP",
        }
        widgets = {
            'ctime': forms.DateInput(
                attrs={'type': 'date',}
            ),
            'utime': forms.DateInput(
                attrs={'type': 'date', }
            ),
            'ps': forms.Textarea(
                attrs={'cols': 80, 'rows': 3}
            ),
            'platform': forms.Select(
                attrs={'class': 'select2',
                       'data-placeholder': ('----请选择平台----')}),

        }
        help_texts = {
            'network_ip': '* 必填项目,唯一值',
            'manager': '* 必填项目',
            "ctime":'* 必填项目',
            "utime":'* 必填项目'
        }
        error_messages = {
            'model':{
                'max_length': ('太短了'),
            }
        }


