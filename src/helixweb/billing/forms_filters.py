from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms_filters import (FilterForm, AbstractFilterActionLogsForm,
    AbstractFilterAllActionLogsForm, AbstractFilterSelfActionLogsForm,
    AbstractFilterUserActionLogsForm)
from helixweb.core.forms import HelixwebRequestForm


class FilterBillingForm(FilterForm, HelixwebRequestForm):
    pass


class AbstractBillingFilterActionLogsForm(AbstractFilterActionLogsForm, FilterBillingForm):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = (
            ('', ''), ('modify_used_currencies', _('modify currencies')),
        )
        super(AbstractBillingFilterActionLogsForm, self).__init__(*args, **kwargs)


class FilterAllActionLogsForm(AbstractBillingFilterActionLogsForm, AbstractFilterAllActionLogsForm):
    pass


class FilterSelfActionLogsForm(AbstractBillingFilterActionLogsForm, AbstractFilterSelfActionLogsForm):
    pass


class FilterUserActionLogsForm(AbstractBillingFilterActionLogsForm, AbstractFilterUserActionLogsForm):
    pass


class FilterBalanceForm(FilterBillingForm):
    action = 'get_balances'
    user_id = forms.CharField(label=_('user id'), max_length=32,
        required=False)
    is_active = forms.ChoiceField(label=_('is active'), required=False, widget=forms.widgets.RadioSelect(),
        choices=(('all', _('all')), ('1', _('active')), ('0', _('inactive'))),
        initial='all')
    from_available_real_amount = forms.DecimalField(label=_('real amount from'),
        required=False)
    to_available_real_amount = forms.DecimalField(label=_('real amount to'),
        required=False)
    from_available_virtual_amount = forms.DecimalField(label=_('virtual amount from'),
        required=False)
    to_available_virtual_amount = forms.DecimalField(label=_('virtual amount to'),
        required=False)
    from_overdraft_limit = forms.DecimalField(label=_('overdraft limit from'),
        required=False)
    to_overdraft_limit = forms.DecimalField(label=_('overdraft limit to'),
        required=False)
    from_locked_amount = forms.DecimalField(label=_('locked amount from'),
        required=False)
    to_locked_amount = forms.DecimalField(label=_('locked amount to'),
        required=False)

    def as_helix_request(self):
        d = super(FilterBalanceForm, self).as_helix_request()
        self._strip_filter_param(d, 'user_id')
        self._strip_filter_param(d, 'from_available_real_amount')
        self._strip_filter_param(d, 'to_available_real_amount')
        self._strip_filter_param(d, 'from_available_virtual_amount')
        self._strip_filter_param(d, 'to_available_virtual_amount')
        self._strip_filter_param(d, 'from_overdraft_limit')
        self._strip_filter_param(d, 'to_overdraft_limit')
        self._strip_filter_param(d, 'from_locked_amount')
        self._strip_filter_param(d, 'to_locked_amount')
        if (not d['filter_params']['is_active'] or
            d['filter_params']['is_active'] == 'all'):
            d['filter_params'].pop('is_active')
        else:
            val = bool(int(d['filter_params']['is_active']))
            d['filter_params']['is_active'] = val
        return d
