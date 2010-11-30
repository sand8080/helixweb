from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms import HelixwebRequestForm
from helixweb.auth import settings


class AuthForm(HelixwebRequestForm):
    def __init__(self, *args, **kwargs):
        kwargs['service_url'] = settings.AUTH_SERVICE_URL
        super(AuthForm, self).__init__(*args, **kwargs)


class LoginForm(AuthForm):
    def __init__(self, *args, **kwargs):
        kwargs['action'] = 'login'
        super(LoginForm, self).__init__(*args, **kwargs)

    environment_name = forms.CharField(label=_('environment name'), max_length=32)
    login = forms.CharField(label=_('user login'))
    password = forms.CharField(label=_('password'), max_length=32)

