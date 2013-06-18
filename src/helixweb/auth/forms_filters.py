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
        self._strip_filter_param(d, 'type')
        self._strip_choice_filter_param(d, 'is_active')
        if 'is_active' in d['filter_params']:
            d['filter_params']['is_active'] = bool(int(d['filter_params']['is_active']))
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
        self._strip_filter_param(d, 'name')
        self._strip_choice_filter_param(d, 'is_active')
        if 'is_active' in d['filter_params']:
            d['filter_params']['is_active'] = bool(int(d['filter_params']['is_active']))
        return d


class FilterUserForm(FilterAuthForm):
    email = forms.CharField(label=_('email'), max_length=32,
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
        self._strip_filter_param(d, 'email')
        self._strip_filter_param(d, 'id')
        self._strip_choice_filter_param(d, 'is_active')
        if 'is_active' in d['filter_params']:
            d['filter_params']['is_active'] = bool(int(d['filter_params']['is_active']))
        return d

class FilterNotificationForm(FilterAuthForm):
    event = forms.CharField(label=_('event'), max_length=32,
        required=False)
    type = forms.ChoiceField(label=_('type'), required=False, # @ReservedAssignment
        widget=forms.widgets.Select(),
        choices=(('all', _('all')), ('email', _('email')),),
        initial='all')

    def __init__(self, *args, **kwargs):
        self.action = 'get_notifications'
        super(FilterNotificationForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(FilterNotificationForm, self).as_helix_request()
        self._strip_filter_param(d, 'event')
        self._strip_choice_filter_param(d, 'type')
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
            ('delete_service', _('delete service')),
            ('add_group', _('add group')),
            ('modify_group', _('modify group')),
            ('delete_group', _('delete group')),
            ('add_user', _('add user')),
            ('register_user', _('register user')),
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
