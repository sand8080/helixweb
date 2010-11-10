from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.client import Client
from helixweb.auth import settings


class HelixwebRequestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # TODO: remove url hardcode
        url = kwargs.pop('service_url')
        super(HelixwebRequestForm, self).__init__(*args, **kwargs)
        self.c = Client(url)

    def request(self, action, session_id=None):
        d = dict(self.cleaned_data)
        d.pop('c', None)
        d['action'] = action
        d['custom_actor_info'] = __package__

        print self.c.request(d)


class LoginForm(HelixwebRequestForm):
    def __init__(self, *args, **kwargs):
        kwargs['service_url'] = settings.AUTH_SERVICE_URL
        super(LoginForm, self).__init__(*args, **kwargs)

    environment_name = forms.CharField(label=_('env name'), max_length=32)
    login = forms.CharField(label=_('login'))
    password = forms.CharField(label=_('password'), max_length=32,
        widget=forms.PasswordInput(render_value=False))
