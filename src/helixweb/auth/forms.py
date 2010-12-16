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
        request = kwargs['request']
        request.COOKIES['session_id'] = None
        super(LoginForm, self).__init__(*args, **kwargs)

    environment_name = forms.CharField(label=_('environment name'), max_length=32)
    login = forms.CharField(label=_('user login'))
    password = forms.CharField(label=_('password'), max_length=32)


class ServiceForm(AuthForm):
    name = forms.CharField(label=_('service name'), max_length=32)
    type = forms.CharField(label=_('service type'), max_length=32)
    properties = forms.CharField(label=_('service functions'),
        widget=forms.Textarea(attrs={'cols': 20, 'rows': 10}))
    is_active = forms.BooleanField(label=_('is active'), initial=True)

    def _get_cleaned_data(self):
        d = super(ServiceForm, self)._get_cleaned_data()
        d['properties'] = self._prepare_properties(d.get('properties', ''))
        return d

    def _prepare_properties(self, s):
        def clean_prop(p):
            res = p.replace('\r', '')
            return res.strip()
        props = map(clean_prop, s.split('\n'))
        props = filter(len, props)
        return props


class AddServiceForm(ServiceForm):
    def __init__(self, *args, **kwargs):
        kwargs['action'] = 'add_service'
        super(AddServiceForm, self).__init__(*args, **kwargs)


class ModifyServiceForm(ServiceForm):
    def __init__(self, *args, **kwargs):
        kwargs['action'] = 'modify_service'
        super(ModifyServiceForm, self).__init__(*args, **kwargs)
