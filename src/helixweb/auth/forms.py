from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms import HelixwebRequestForm, _get_session_id
from helixweb.core.widgets import ServicesSelectMultiple, ConstInput


class LoginForm(HelixwebRequestForm):
    action = 'login'
    environment_name = forms.CharField(label=_("environment"),
        max_length=32)
    email = forms.CharField(label=_("email"),
        max_length=32)
    password = forms.CharField(label=_("password"),
        max_length=32, widget=forms.PasswordInput)
    bind_to_ip = forms.BooleanField(label=_("bind session to ip"),
        required=False)
    fixed_lifetime_minutes = forms.ChoiceField(label=_("session lifetime"),
        choices=((None, ""), ('15', _("15 minutes")), ('60', _("1 hour")),
            ('120', _("2 hours"))),
        initial='', required=False)

    def __init__(self, *args, **kwargs):
        request = kwargs['request']
        request.COOKIES['session_id'] = None
        super(LoginForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(LoginForm, self).as_helix_request()
        d.pop('session_id', None)
        self._strip_bool_param(d, 'bind_to_ip')
        self._strip_int_param(d, 'fixed_lifetime_minutes')
        return d


class LogoutForm(HelixwebRequestForm):
    action = 'logout'


class ServiceForm(HelixwebRequestForm):
    def _prepare_properties(self, s):
        def clean_prop(p):
            res = p.replace('\r', '')
            return res.strip()
        props = map(clean_prop, s.split('\n'))
        props = filter(len, props)
        return props

    @staticmethod
    def get_by_id_req(id, request): #@ReservedAssignment
        return {'action': 'get_services', 'session_id': _get_session_id(request),
            'filter_params': {'id': int(id)}, 'paging_params':{}}


class AddServiceForm(ServiceForm):
    action = 'add_service'
    name = forms.CharField(label=_('service name'), max_length=32)
    type = forms.CharField(label=_('service type'), max_length=32) #@ReservedAssignment
    properties = forms.CharField(label=_('service functions'),
        widget=forms.Textarea(attrs={'cols': 20, 'rows': 10}))
    is_active = forms.BooleanField(label=_('is active'), initial=True,
        required=False)

    def as_helix_request(self):
        d = super(AddServiceForm, self).as_helix_request()
        d['properties'] = self._prepare_properties(d.get('properties', ''))
        return d


class DeleteServiceForm(ServiceForm):
    action = 'delete_service'
    id = forms.IntegerField(widget=forms.widgets.HiddenInput) #@ReservedAssignment
    name = forms.CharField(label=_('service name'), max_length=32,
        widget=ConstInput)

    def __init__(self, *args, **kwargs):
        super(DeleteServiceForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(DeleteServiceForm, self).as_helix_request()
        d.pop('name')
        return d


class ModifyServiceForm(ServiceForm):
    action = 'modify_service'
    id = forms.IntegerField(widget=forms.widgets.HiddenInput) #@ReservedAssignment
    new_name = forms.CharField(label=_('service name'), max_length=32)
    type = forms.CharField(label=_('service type'), widget=ConstInput) #@ReservedAssignment
    new_properties = forms.CharField(label=_('service functions'),
        widget=forms.Textarea(attrs={'cols': 20, 'rows': 10}), required=False)
    new_is_active = forms.BooleanField(label=_('is active'), required=False)

    def as_helix_request(self):
        d = super(ModifyServiceForm, self).as_helix_request()
        d['new_properties'] = self._prepare_properties(d.get('new_properties', ''))
        d.pop('type')
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
        d['type'] = srv_d.get('type')
        return ModifyServiceForm(d, request=request)

    @staticmethod
    def get_by_id_req(srv_id, request):
        return {'action': 'get_services', 'session_id': _get_session_id(request),
            'filter_params': {'ids': [int(srv_id)]}, 'paging_params':{}}


class AddEnvironmentForm(HelixwebRequestForm):
    action = 'add_environment'
    name = forms.CharField(label=_('environment'), max_length=32)
    su_email = forms.CharField(label=_('super user email'), max_length=32)
    su_password = forms.CharField(label=_('password'),
        max_length=32, widget=forms.PasswordInput)

    def as_helix_request(self):
        d = super(AddEnvironmentForm, self).as_helix_request()
        d.pop('session_id', None)
        return d


class ModifyEnvironmentForm(HelixwebRequestForm):
    action = 'modify_environment'
    new_name = forms.CharField(label=_('environment name'), max_length=32)

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


class AddUserForm(HelixwebRequestForm):
    action = 'add_user'
    email = forms.CharField(label=_('email'), max_length=32)
    password = forms.CharField(label=_('password'),
        max_length=32, widget=forms.PasswordInput)
    is_active = forms.BooleanField(label=_('is active'), initial=True,
        required=False)

    def __init__(self, *args, **kwargs):
        groups = kwargs.pop('groups', [])
        super(AddUserForm, self).__init__(*args, **kwargs)
        choices = [(g['id'], g['name']) for g in groups]
        self.fields['groups_ids'] = forms.MultipleChoiceField(label=_('groups'),
            required=False, choices=choices, initial=self.initial_groups(choices),
            widget=forms.widgets.CheckboxSelectMultiple)

    def initial_groups(self, choices, groups=('Users', 'Billing Users')):
        result = filter(lambda x: x[1] in groups, choices)
        return [x[0] for x in result]

    def as_helix_request(self):
        d = super(AddUserForm, self).as_helix_request()
        d['groups_ids'] = map(int, d['groups_ids'])
        return d


class ModifyUserForm(HelixwebRequestForm):
    action = 'modify_users'
    id = forms.IntegerField(widget=forms.widgets.HiddenInput) #@ReservedAssignment
    new_email = forms.CharField(label=_('email'), max_length=32,
        required=False)
    new_password = forms.CharField(label=_('password'),
        max_length=32, widget=forms.PasswordInput, required=False)
    new_is_active = forms.BooleanField(label=_('is active'), initial=True,
        required=False)

    def __init__(self, *args, **kwargs):
        groups = kwargs.pop('groups', [])
        super(ModifyUserForm, self).__init__(*args, **kwargs)
        choices = [(g['id'], g['name']) for g in groups]
        self.fields['new_groups_ids'] = forms.MultipleChoiceField(label=_('groups'),
            required=False, choices=choices,
            widget=forms.widgets.CheckboxSelectMultiple)

    def as_helix_request(self):
        d = super(ModifyUserForm, self).as_helix_request()
        id = d.pop('id') #@ReservedAssignment
        d['ids'] = [id]
        d['new_groups_ids'] = map(int, d['new_groups_ids'])
        self._strip_param(d, 'new_email')
        self._strip_param(d, 'new_password')
        return d

    @staticmethod
    def get_users_req(user_id, request):
        return {'action': 'get_users', 'session_id': _get_session_id(request),
            'filter_params': {'ids': [int(user_id)]}, 'paging_params':{}}

    @staticmethod
    def from_user_info(user_info, groups, request):
        u_d = dict(user_info)
        id = u_d.pop('id', None) #@ReservedAssignment
        d = {'id': id}
        for k in u_d.keys():
            d['new_%s' % k] = u_d[k]
        return ModifyUserForm(d, request=request, groups=groups)


class ModifyUserSelfForm(HelixwebRequestForm):
    action ='modify_user_self'
    old_password = forms.CharField(label=_('old password'),
        max_length=32, widget=forms.PasswordInput)
    new_password = forms.CharField(label=_('new password'),
        max_length=32, widget=forms.PasswordInput)


class GroupForm(HelixwebRequestForm):
    @staticmethod
    def get_by_id_req(id, request): #@ReservedAssignment
        return {'action': 'get_groups', 'session_id': _get_session_id(request),
            'filter_params': {'ids': [int(id)]}, 'paging_params':{}}


class AddGroupForm(GroupForm):
    action = 'add_group'
    name = forms.CharField(label=_('group name'), max_length=32)
    is_active = forms.BooleanField(label=_('is active'), initial=True,
        required=False)

    def __init__(self, *args, **kwargs):
        services = kwargs.pop('services', [])
        super(AddGroupForm, self).__init__(*args, **kwargs)
        self.fields['rights'] = forms.CharField(label=_('group rights'),
            widget=ServicesSelectMultiple(*args, services=services), required=False)

    def as_helix_request(self):
        d = super(AddGroupForm, self).as_helix_request()
        d['rights'] = self.fields['rights'].widget.as_helix_request()
        return d


class DeleteGroupForm(GroupForm):
    action = 'delete_group'
    id = forms.IntegerField(widget=forms.widgets.HiddenInput) #@ReservedAssignment
    name = forms.CharField(label=_('group name'), max_length=32,
        widget=ConstInput)

    def __init__(self, *args, **kwargs):
        super(DeleteGroupForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(DeleteGroupForm, self).as_helix_request()
        d.pop('name')
        return d


class ModifyGroupForm(GroupForm):
    action = 'modify_group'
    id = forms.IntegerField(widget=forms.widgets.HiddenInput) #@ReservedAssignment
    new_name = forms.CharField(label=_('group name'), max_length=32)
    new_is_active = forms.BooleanField(label=_('is active'), required=False)

    def __init__(self, *args, **kwargs):
        services = kwargs.pop('services', [])
        super(ModifyGroupForm, self).__init__(*args, **kwargs)
        self.fields['new_rights'] = forms.CharField(label=_('group rights'),
            widget=ServicesSelectMultiple(*args, services=services), required=False)

    def as_helix_request(self):
        d = super(ModifyGroupForm, self).as_helix_request()
        d['new_rights'] = self.fields['new_rights'].widget.as_helix_request()
        return d

    @staticmethod
    def from_get_groups_helix_resp(helix_resp, request, services):
        d = helix_resp.get('groups', [{'id': 0}])[0]
        res_d = {}
        for k in d.keys():
            if k not in ('id', ):
                res_d['new_%s' % k] = d[k]
            else:
                res_d[k] = d[k]
        for srv in res_d.pop('new_rights', []):
            for p in srv['properties']:
                res_d['%s_%s' % (srv['service_id'], p)] = ''
        return ModifyGroupForm(res_d, request=request, services=services)


class ApiSchemeForm(HelixwebRequestForm):
    action = 'get_api_scheme'
