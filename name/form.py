from django import forms

from name.models import Names



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