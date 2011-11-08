from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms_filters import (FilterForm, AbstractFilterActionLogsForm,
    AbstractFilterAllActionLogsForm, AbstractFilterSelfActionLogsForm,
    AbstractFilterUserActionLogsForm)
from helixweb.core.forms import HelixwebRequestForm


class FilterAuthForm(FilterForm, HelixwebRequestForm):
    pass


class FilterServiceForm(FilterAuthForm):
    type = forms.CharField(label=_('service type'), max_length=32, #@ReservedAssignment
        required=False)
    is_active = forms.ChoiceField(label=_('is active'), required=False, widget=forms.widgets.RadioSelect(),
        choices=(('all', _('all')), ('1', _('active')), ('0', _('inactive'))),
        initial='all')

    def __init__(self, *args, **kwargs):
        self.action = 'get_services'
        super(FilterServiceForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(FilterServiceForm, self).as_helix_request()
        s_t = d['filter_params'].pop('type').strip()
        if len(s_t):
            d['filter_params']['type'] = s_t
        if d['filter_params']['is_active'] == 'all':
            d['filter_params'].pop('is_active')
        else:
            val = bool(int(d['filter_params']['is_active']))
            d['filter_params']['is_active'] = val
        return d


class FilterGroupForm(FilterAuthForm):
    name = forms.CharField(label=_('group name'), max_length=32,
        required=False)
    is_active = forms.ChoiceField(label=_('is active'), required=False, widget=forms.widgets.RadioSelect(),
        choices=(('all', _('all')), ('1', _('active')), ('0', _('inactive'))),
        initial='all')

    def __init__(self, *args, **kwargs):
        self.action = 'get_groups'
        super(FilterGroupForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(FilterGroupForm, self).as_helix_request()
        s_t = d['filter_params'].pop('name').strip()
        if len(s_t):
            d['filter_params']['name'] = s_t
        if d['filter_params']['is_active'] == 'all':
            d['filter_params'].pop('is_active')
        else:
            val = bool(int(d['filter_params']['is_active']))
            d['filter_params']['is_active'] = val
        return d


class FilterUserForm(FilterAuthForm):
    login = forms.CharField(label=_('login'), max_length=32,
        required=False)
    id = forms.IntegerField(label=_('id'), required=False) #@ReservedAssignment
    is_active = forms.ChoiceField(label=_('is active'), required=False, widget=forms.widgets.RadioSelect(),
        choices=(('all', _('all')), ('1', _('active')), ('0', _('inactive'))),
        initial='all')

    def __init__(self, *args, **kwargs):
        self.action = 'get_users'
        super(FilterUserForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(FilterUserForm, self).as_helix_request()
        self._strip_filter_param(d, 'login')
        self._strip_filter_param(d, 'id')
        if (not d['filter_params']['is_active'] or
            d['filter_params']['is_active'] == 'all'):
            d['filter_params'].pop('is_active')
        else:
            val = bool(int(d['filter_params']['is_active']))
            d['filter_params']['is_active'] = val
        return d


class AbstractAuthFilterActionLogsForm(AbstractFilterActionLogsForm, FilterAuthForm):
    action = 'get_action_logs'
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = (
            ('', ''), ('login', _('login')), ('logout', _('logout')),
            ('add_environment', _('add environment')),
            ('modify_environment', _('modify environment')),
            ('add_service', _('add service')),
            ('modify_service', _('modify service')),
            ('add_group', _('add group')),
            ('modify_group', _('modify group')),
            ('delete_group', _('delete group')),
            ('add_user', _('add user')),
            ('modify_uses', _('modify users')),
            ('modify_user_self', _('modify user self')),
        )
        super(AbstractAuthFilterActionLogsForm, self).__init__(*args, **kwargs)


class FilterAllActionLogsForm(AbstractAuthFilterActionLogsForm, AbstractFilterAllActionLogsForm):
    pass


class FilterSelfActionLogsForm(AbstractAuthFilterActionLogsForm, AbstractFilterSelfActionLogsForm):
    pass


class FilterUserActionLogsForm(AbstractAuthFilterActionLogsForm, AbstractFilterUserActionLogsForm):
    pass