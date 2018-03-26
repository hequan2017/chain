from    django import forms
from   .models import asset,asset_user


class FileForm(forms.Form):
    file = forms.FileField(label="导入资产")


class AssetForm(forms.ModelForm):


    class Meta:
        model = asset
        fields = '__all__'

        labels = {
            "network_ip": "外网IP",
        }
        widgets = {
            'buy_time': forms.DateInput(
                attrs={'type': 'date', }
            ),
            'expire_time': forms.DateInput(
                attrs={'type': 'date', }
            ),
            'ps': forms.Textarea(
                attrs={'cols': 80, 'rows': 3}),
            'private_key': forms.Textarea(
                attrs={'cols': 80, 'rows': 8}
            ),
            'platform': forms.Select(
                attrs={'class': 'select2',
                       'data-placeholder': ('----请选择平台----')}),
            'manager': forms.Select(
                attrs={'class': 'select2',
                       'data-placeholder': ('----请选择负责人----')}),
            'region': forms.Select(
                attrs={'class': 'select2',
                       'data-placeholder': ('----请选择区域----')}),
            'project': forms.Select(
                attrs={'class': 'select2',
                       'data-placeholder': ('----请选择项目----')}),
            'user': forms.Select(
                attrs={'class': 'select2',
                       'data-placeholder': ('----请选择登录用户----')}),
        }

        help_texts = {
            'hostname': '*  必填项目,名字唯一',
            'platform': '*  必填项目',
            'region': '*  必填项目',
            'manager': '*  必填项目',
            'project': '*  必填项目'
        }
        error_messages = {
            'model': {
                'max_length': ('太短了'),
            }
        }





class AssetUserForm(forms.ModelForm):


    class Meta:
        model = asset_user
        fields = '__all__'


        widgets = {
            'password': forms.PasswordInput(
            ),
            'ps': forms.Textarea(
                attrs={'cols': 80, 'rows': 3}),
        }


