from django import forms


class UserPasswordForm(forms.Form):
    old_password = forms.CharField(max_length=128, widget=forms.PasswordInput, label='旧密码')
    new_password = forms.CharField(min_length=5, max_length=128, widget=forms.PasswordInput, label='新密码',
                                   help_text="* 最少为5个字符")
    confirm_password = forms.CharField(min_length=5, max_length=128, widget=forms.PasswordInput, label='确认密码',
                                       help_text="* 最少为5个字符")

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not self.instance.check_password(old_password):
            raise forms.ValidationError('旧密码错误')
        return old_password

    def clean_confirm_password(self):
        new_password = self.cleaned_data['new_password']
        confirm_password = self.cleaned_data['confirm_password']

        if new_password != confirm_password:
            raise forms.ValidationError('新密码与确认密码不一致')
        return confirm_password

    def save(self):
        password = self.cleaned_data['new_password']
        self.instance.set_password(password)
        self.instance.save()
        return self.instance