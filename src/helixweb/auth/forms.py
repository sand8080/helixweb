from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms import HelixwebRequestForm, _get_session_id


class LoginForm(HelixwebRequestForm):
    def __init__(self, *args, **kwargs):
        self.action = 'login'
        request = kwargs['request']
        request.COOKIES['session_id'] = None
        super(LoginForm, self).__init__(*args, **kwargs)

    environment_name = forms.CharField(label=_('environment name'), max_length=32)
    login = forms.CharField(label=_('user login'))
    password = forms.CharField(label=_('password'), max_length=32)


class ServiceForm(HelixwebRequestForm):
    def _prepare_properties(self, s):
        def clean_prop(p):
            res = p.replace('\r', '')
            return res.strip()
        props = map(clean_prop, s.split('\n'))
        props = filter(len, props)
        return props


class AddServiceForm(ServiceForm):
    name = forms.CharField(label=_('service name'), max_length=32)
    type = forms.CharField(label=_('service type'), max_length=32)
    properties = forms.CharField(label=_('service functions'),
        widget=forms.Textarea(attrs={'cols': 20, 'rows': 10}))
    is_active = forms.BooleanField(label=_('is active'), initial=True,
        required=False)

    def __init__(self, *args, **kwargs):
        self.action = 'add_service'
        super(AddServiceForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(AddServiceForm, self).as_helix_request()
        d['properties'] = self._prepare_properties(d.get('properties', ''))
        return d


class ModifyServiceForm(ServiceForm):
    id = forms.IntegerField(widget=forms.widgets.HiddenInput)
    new_name = forms.CharField(label=_('service name'), max_length=32)
    new_properties = forms.CharField(label=_('service functions'),
        widget=forms.Textarea(attrs={'cols': 20, 'rows': 10}), required=False)
    new_is_active = forms.BooleanField(label=_('is active'), required=False)
    action = 'modify_service'

    def __init__(self, *args, **kwargs):
        super(ModifyServiceForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(ModifyServiceForm, self).as_helix_request()
        d['new_properties'] = self._prepare_properties(d.get('new_properties', ''))
        return d

    @staticmethod
    def from_get_services_helix_resp(helix_resp, request):
        srv_d = helix_resp.get('services', [{'service_id': 0}])[0]
        d = {}
        for k in srv_d.keys():
            if k not in ('id', ):
                d['new_%s' % k] = srv_d[k]
            else:
                d[k] = srv_d[k]
        d['new_properties'] = '\n'.join(d['new_properties'])
        return ModifyServiceForm(d, request=request)

    @staticmethod
    def get_by_id_req(srv_id, request):
        return {'action': 'get_services', 'session_id': _get_session_id(request),
            'filter_params': {'ids': [int(srv_id)]}, 'paging_params':{}}


class ModifyEnvironmentForm(HelixwebRequestForm):
    new_name = forms.CharField(label=_('environment name'), max_length=32)
    action = 'modify_environment'

    def __init__(self, *args, **kwargs):
        super(ModifyEnvironmentForm, self).__init__(*args, **kwargs)

    @staticmethod
    def get_req(request):
        return {'action': 'get_environment',
            'session_id': _get_session_id(request)}

    @staticmethod
    def from_get_helix_resp(helix_resp, request):
        env_d = helix_resp.get('environment', {})
        d = {}
        for k in env_d.keys():
            d['new_%s' % k] = env_d[k]
        return ModifyEnvironmentForm(d, request=request)
