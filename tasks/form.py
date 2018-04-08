from    django import forms
from .models import tools_script


class ToolsForm(forms.ModelForm):
    class Meta:
        model = tools_script
        fields = '__all__'
        widgets = {
            'comment': forms.Textarea(
                attrs={'cols': 80, 'rows': 6}
            ),
            'tool_script': forms.Textarea(
            ),
            'tool_run_type': forms.Select(
                attrs={'class': 'select2',
                       'data-placeholder': ('选择脚本类型')}),
        }
        help_texts = {
            'name': ('* 必填项目,名字不可以重复'),
            'tool_script':('* python脚本 开头必须要写 #!/usr/bin/python')
        }


