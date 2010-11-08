from django import forms
from django.utils.translation import ugettext_lazy as _


class LoginForm(forms.Form):
    environment_name = forms.CharField(label=_(u'Env name'), max_length=32)
    login = forms.EmailField(localize=True)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False),
        max_length=32)
    password_confirm = forms.CharField(widget=forms.PasswordInput(render_value=False),
        max_length=32, required=False)