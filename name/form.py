from django import forms
from name.models import Names, Groups
from guardian.models import GroupObjectPermission
from asset.models import AssetProject
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission


class NameForm(forms.ModelForm):
    class Meta:
        model = Names
        fields = '__all__'

        help_texts = {
            'password': '* 如不修改密码，请输入 1 ',
        }

        widgets = {
            'password': forms.PasswordInput(
            ),
            'date_joined': forms.DateTimeInput(),
            'ps': forms.Textarea(
                attrs={'cols': 80, 'rows': 3}),

        }


class GroupsForm(forms.ModelForm):
    class Meta:
        model = Groups
        fields = '__all__'

        widgets = {
            'ps': forms.Textarea(
                attrs={'cols': 80, 'rows': 3}),
        }


class GroupsObjectForm(forms.ModelForm):
    object_pk = forms.ModelChoiceField(
        queryset=AssetProject.objects.all(),
        label="资产项目",
        widget=forms.Select(
            attrs={
                'data-placeholder': '--------请选择资产项目--------',
            }
        ),
    )
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(model="assetproject"),
        label="权限类型",
        widget=forms.Select(
            attrs={
                'data-placeholder': '--------请选择权限类型--------',
            }
        ),
    )

    permission = forms.ModelChoiceField(
        queryset=Permission.objects.filter(content_type__model="assetproject"),
        label="权限",
        widget=forms.Select(
            attrs={
                'data-placeholder': '--------请选择权限--------',
            }
        ),
    )

    class Meta:
        model = GroupObjectPermission
        fields = '__all__'

        labels = {
            'group': '系统组',
        }

    def clean_object_pk(self):
        obj = self.cleaned_data.get('object_pk')
        ret = AssetProject.objects.get(projects=obj).id
        return ret
