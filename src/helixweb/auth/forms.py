from django import forms
from django.utils.translation import ugettext_lazy as _


class LoginForm(forms.Form):
    environment_name = forms.CharField(label=_('env name'), max_length=32)
    login = forms.EmailField(label=_('login'))
    password = forms.CharField(label=_('password'), max_length=32,
        widget=forms.PasswordInput(render_value=False))
    password_confirm = forms.CharField(label=_('confirm password'),
        max_length=32, required=False,
        widget=forms.PasswordInput(render_value=False))
