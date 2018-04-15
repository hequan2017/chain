from django import forms
from asset.models import AssetInfo, AssetLoginUser
from tasks.models import Variable


class FileForm(forms.Form):
    file = forms.FileField(label="导入资产")


class AssetForm(forms.ModelForm):
    vars = forms.ModelMultipleChoiceField(
        queryset=Variable.objects.all(),
        label="变量组",
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': '--------请选择变量组--------',
            }
        ),
        required=False,
    )

    def __init__(self, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('initial', {})
            initial.update({
                'vars': instance.asset.all(),
            })
            kwargs['initial'] = initial
        super().__init__(**kwargs)

    def save(self, commit=True):
        var = super().save(commit=commit)
        users = self.cleaned_data['vars']
        var.asset.set(users)
        return var

    class Meta:
        model = AssetInfo
        # fields = '__all__'
        fields = [
            'hostname',
            'network_ip',
            'inner_ip',
            'system',
            'vars',
            'cpu',
            'memory',
            'disk',
            'bandwidth',
            'project',
            'platform',
            'region',
            'manager',
            'user',
            'Instance_id',
            'buy_time',
            'expire_time',
            'port',
            'ps',
            'is_active']

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
                       'data-placeholder': '----请选择平台----'}),
            'manager': forms.Select(
                attrs={'class': 'select2',
                       'data-placeholder': '----请选择负责人----'}),
            'region': forms.Select(
                attrs={'class': 'select2',
                       'data-placeholder': '----请选择区域----'}),
            'project': forms.Select(
                attrs={'class': 'select2',
                       'data-placeholder': '----请选择项目----'}),
            'user': forms.Select(
                attrs={'class': 'select2',
                       'data-placeholder': '----请选择登录用户----'}),
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
                'max_length': ('太短了', ),
            }
        }


class AssetUserForm(forms.ModelForm):
    class Meta:
        model = AssetLoginUser
        fields = '__all__'

        help_texts = {
            'password': '* 如不修改密码，请保持为空',
            'private_key': '*  如私钥有密码，请先取消掉再上传',
        }

        widgets = {
            'password': forms.PasswordInput(
            ),
            'ps': forms.Textarea(
                attrs={'cols': 80, 'rows': 3}),
        }
