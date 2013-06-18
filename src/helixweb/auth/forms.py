from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms import HelixwebRequestForm, _get_session_id
from helixweb.core.widgets import ServicesSelectMultiple, ConstInput

from helixweb.auth import settings


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
        request.COOKIES['login_with_env'] = None
        super(LoginForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(LoginForm, self).as_helix_request()
        d.pop('session_id', None)
        self._strip_bool_param(d, 'bind_to_ip')
        self._strip_int_param(d, 'fixed_lifetime_minutes')
        return d


class LoginEnvForm(LoginForm):
    def __init__(self, *args, **kwargs):
        env_name = kwargs.pop('env_name', None)
        super(LoginEnvForm, self).__init__(*args, **kwargs)
        self.fields['environment_name'] = forms.CharField(widget=forms.widgets.HiddenInput,
                        initial=env_name)


class LogoutForm(HelixwebRequestForm):
    action = 'logout'


class RegisterUserForm(HelixwebRequestForm):
    action = 'register_user'
    environment_name = forms.CharField(label=_("environment"),
        max_length=32)
    email = forms.CharField(label=_("email"),
        max_length=32)
    password = forms.CharField(label=_("password"),
        max_length=32, widget=forms.PasswordInput)
    lang = forms.ChoiceField(label=_('notifications lang'), choices=(settings.LANGS),
        initial=settings.DEFAULT_LANG)

    def __init__(self, *args, **kwargs):
        request = kwargs['request']
        request.COOKIES['session_id'] = None
        request.COOKIES['login_with_env'] = None
        super(RegisterUserForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(RegisterUserForm, self).as_helix_request()
        d.pop('session_id', None)
        return d


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
    lang = forms.ChoiceField(label=_('notifications lang'), choices=(settings.LANGS),
        initial=settings.DEFAULT_LANG)

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
    new_lang = forms.ChoiceField(label=_('notifications lang'), choices=(settings.LANGS),
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
        self._strip_param(d, 'new_lang')
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
        max_length=32, widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(label=_('new password'),
        max_length=32, widget=forms.PasswordInput, required=False)
    new_lang = forms.ChoiceField(label=_('notifications lang'),
        choices=settings.LANGS, required=False)

    def as_helix_request(self):
        d = super(ModifyUserSelfForm, self).as_helix_request()
        self._strip_param(d, 'old_password')
        self._strip_param(d, 'new_password')
        self._strip_param(d, 'new_lang')
        return d

    @staticmethod
    def from_get_user_helix_resp(helix_resp, request):
        d = helix_resp.get('user', {})
        d['new_lang'] = d.get('lang')
        return ModifyUserSelfForm(d, request=request)


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
    is_default = forms.BooleanField(label=_('is default'), initial=False,
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
    new_is_default = forms.BooleanField(label=_('is default'), required=False)

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


class ModifyNotificationForm(HelixwebRequestForm):
    action = 'modify_notifications'
    _message_field_prefix = 'message_'

    def __init__(self, *args, **kwargs):
        d = args[0]
        super(ModifyNotificationForm, self).__init__(*args, **kwargs)
        self.fields['id'] = forms.IntegerField(widget=forms.widgets.HiddenInput)
        self.fields['is_active'] = forms.BooleanField(label=_('is active'),
                        required=False)
        msg_f_names = self._filter_message_names(d)
        self._generate_message_fields(msg_f_names)

    def _filter_message_names(self, d):
        return filter(lambda x: x.startswith(self._message_field_prefix), d.keys())

    def _group_message_field_names(self, msg_f_names):
        grp_msgs = dict()
        for f_name in msg_f_names:
            head = len(self._message_field_prefix)
            tail = f_name.rfind('_')
            f_n = f_name[head:tail]
            try:
                idx = int(f_name[tail + 1:])
                if idx not in grp_msgs:
                    grp_msgs[idx] = list()
                grp_msgs[idx].append(f_n)
            except Exception:
                pass
        return grp_msgs

    def _generate_message_fields(self, msg_f_names):
        idxs = self._group_message_field_names(msg_f_names)
        for k in sorted(idxs.keys()):
            if 'lang' in idxs[k]:
                self.fields[self._message_field_name('lang', k)] = forms.CharField(
                            label=_('language'), widget=ConstInput, required=False)
            if 'email_subj' in idxs[k]:
                self.fields[self._message_field_name('email_subj', k)] = forms.CharField(
                            label=_('subject'), required=False,
                            widget=forms.TextInput(attrs={'size':'60', 'class':'inputText'}))
            if 'email_msg' in idxs[k]:
                self.fields[self._message_field_name('email_msg', k)] = forms.CharField(
                            label=_('message'), required=False,
                            widget=forms.Textarea(attrs={'cols': 60, 'rows': 10}))

    @staticmethod
    def _message_field_name(f_name, idx):
        return '%s%s_%d' % (ModifyNotificationForm._message_field_prefix, f_name, idx)

    @staticmethod
    def get_by_id_req(id, request):
        return {'action': 'get_notifications', 'session_id': _get_session_id(request),
            'filter_params': {'ids': [int(id)]}, 'paging_params':{}}

    @staticmethod
    def from_get_notifications_helix_resp(helix_resp, request):
        d = helix_resp.get('notifications', [{'id': 0}])[0]
        res_d = {'id': d.get('id'), 'is_active': d.get('is_active')}
        for i, m in enumerate(d.get('messages', [])):
            for k in m.keys():
                res_d[ModifyNotificationForm._message_field_name(k, i)] = m.get(k)
        return ModifyNotificationForm(res_d, request=request)

    def as_helix_request(self):
        d = super(ModifyNotificationForm, self).as_helix_request()
        id = d.pop('id')
        d['ids'] = [id]
        self._strip_bool_param(d, 'is_active', 'new_is_active')
        new_messages = list()
        msg_f_names_idx = self._group_message_field_names(d.keys())
        for idx, f_names in msg_f_names_idx.items():
            msg = dict()
            for f_name in f_names:
                msg[f_name] = d.pop(self._message_field_name(f_name, idx))
            new_messages.append(msg)
        if len(new_messages) > 0:
            d['new_messages'] = new_messages
        return d

