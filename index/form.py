from django import forms


class UserPasswordForm(forms.Form):
    old_password = forms.CharField(max_length=128, widget=forms.PasswordInput, label='旧密码')
    new_password = forms.CharField(min_length=5,max_length=128, widget=forms.PasswordInput,label='新密码',help_text="* 最少为5个字符")
    confirm_password = forms.CharField(min_length=5,max_length=128,widget=forms.PasswordInput,label='确认密码',help_text="* 最少为5个字符")


    # def clean(self):
    #     cleaned_data = super().clean()
    #
    #     password1 = cleaned_data.get('new_password')
    #     password2 = cleaned_data.get('confirm_password')
    #
    #     if password1 and password2:
    #         if password1 != password2:
    #             self._errors['password'] = self.error_class(["两次密码输入不一致"])
    #
    #     return cleaned_data