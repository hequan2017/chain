from django import forms
from name.models import Names, Groups
from guardian.models import GroupObjectPermission
from asset.models import AssetProject



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

    object_pk1 = forms.ModelChoiceField(
        queryset= AssetProject.objects.all(),
        label="资产项目",
        widget=forms.Select(
            attrs={
                'data-placeholder': '--------请选择资产项目--------',
            }
        ),
    )

    class Meta:
        model = GroupObjectPermission
        fields = '__all__'

        labels = {
            'content_type': '对象类型',
            'group': '组',
            'permission': '权限',
        }
        widgets = {
            'content_type': forms.Select(
            attrs={
                'class': 'select2',
                'data-placeholder': '--------请选择对象类型--------',})
        }

        help_texts = {
            'content_type': '*  对象类型,请与下面选择的权限 对应',

        }


    def clean_object_pk1(self):
        obj = self.cleaned_data.get('object_pk1')
        ret = AssetProject.objects.get(projects=obj).id
        return ret
