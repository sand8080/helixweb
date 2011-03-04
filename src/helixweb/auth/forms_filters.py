from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms_filters import FilterForm
from helixweb.core.forms import HelixwebRequestForm


class FilterAuthForm(FilterForm, HelixwebRequestForm):
    pass


class FilterServiceForm(FilterAuthForm):
    type = forms.CharField(label=_('service type'), max_length=32,
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
    is_active = forms.ChoiceField(label=_('is active'), required=False, widget=forms.widgets.RadioSelect(),
        choices=(('all', _('all')), ('1', _('active')), ('0', _('inactive'))),
        initial='all')

    def __init__(self, *args, **kwargs):
        self.action = 'get_users'
        super(FilterUserForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(FilterUserForm, self).as_helix_request()
        d['filter_params']['roles'] = ['user']
        l = d['filter_params'].pop('login').strip()
        if len(l):
            d['filter_params']['name'] = l
        if d['filter_params']['is_active'] == 'all':
            d['filter_params'].pop('is_active')
        else:
            val = bool(int(d['filter_params']['is_active']))
            d['filter_params']['is_active'] = val
        return d


class FilterActionLogsForm(FilterAuthForm):
    action_name = forms.CharField(label=_('action name'), max_length=32,
        required=False)

    def __init__(self, *args, **kwargs):
        self.action = 'get_action_logs'
        super(FilterActionLogsForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(FilterActionLogsForm, self).as_helix_request()
        action = d['filter_params'].pop('action_name', None)
        if action:
            d['filter_params']['action'] = action
        print '### form as_helix_request', d
        return d

