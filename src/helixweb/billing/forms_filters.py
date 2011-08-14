from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.widgets import ConstInput
from helixweb.core.forms_filters import (FilterForm, AbstractFilterActionLogsForm,
    AbstractFilterAllActionLogsForm, AbstractFilterSelfActionLogsForm,
    AbstractFilterUserActionLogsForm)
from helixweb.billing.forms import BillingForm


class FilterBillingForm(FilterForm, BillingForm):
    pass


class AbstractBillingFilterActionLogsForm(AbstractFilterActionLogsForm, FilterBillingForm):
    action = 'get_action_logs'
    def __init__(self, *args, **kwargs):
        # TODO: add all actions
        kwargs['choices'] = (('', ''),
            ('add_balance', _('add balance')),
            ('modify_used_currencies', _('modify currencies')),
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

    def __init__(self, *args, **kwargs):
        currencies = kwargs.pop('currencies', [])
        super(FilterBalanceForm, self).__init__(*args, **kwargs)

        self.fields['id'] = forms.IntegerField(label=_('balance id'), required=False)
        self.fields['user_id'] = forms.IntegerField(label=_('user id'), required=False)
        self.fields['currency_code'] = self._gen_currency_code(currencies, required=False)
        self.fields['from_real_amount'] = forms.DecimalField(label=_('real amount from'),
            required=False)
        self.fields['to_real_amount'] = forms.DecimalField(label=_('real amount to'),
            required=False)
        self.fields['from_virtual_amount'] = forms.DecimalField(label=_('virtual amount from'),
            required=False)
        self.fields['to_virtual_amount'] = forms.DecimalField(label=_('virtual amount to'),
            required=False)
        self.fields['from_overdraft_limit'] = forms.DecimalField(label=_('overdraft limit from'),
            required=False)
        self.fields['to_overdraft_limit'] = forms.DecimalField(label=_('overdraft limit to'),
            required=False)
        self.fields['from_locked_amount'] = forms.DecimalField(label=_('locked amount from'),
            required=False)
        self.fields['to_locked_amount'] = forms.DecimalField(label=_('locked amount to'),
            required=False)
        self.fields['is_active'] = forms.ChoiceField(label=_('is active'), required=False, widget=forms.widgets.RadioSelect(),
            choices=(('all', _('all')), ('1', _('active')), ('0', _('inactive'))),
            initial='all')

    def as_helix_request(self):
        d = super(FilterBalanceForm, self).as_helix_request()
        self._strip_filter_param(d, 'id')
        self._strip_filter_param(d, 'user_id')
        self._strip_filter_param(d, 'currency_code')
        self._strip_filter_param(d, 'from_real_amount')
        self._strip_filter_param(d, 'to_real_amount')
        self._strip_filter_param(d, 'from_virtual_amount')
        self._strip_filter_param(d, 'to_virtual_amount')
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


class AbstractFilterLocksForm(FilterBillingForm):
    action = 'get_locks'

    def _add_common_fields(self):
        self.fields['order_id'] = forms.CharField(label=_('order id'),
            max_length=64, required=False)
        self.fields['from_creation_date'] = forms.DateField(label=_('from'), required=False)
        self.fields['to_creation_date'] = forms.DateField(label=_('to'), required=False)

    def as_helix_request(self):
        d = super(AbstractFilterLocksForm, self).as_helix_request()
        self._strip_filter_param(d, 'user_id')
        self._strip_filter_param(d, 'order_id')
        self._strip_filter_param(d, 'balance_id')
        self._strip_from_date_param(d, 'from_creation_date')
        self._strip_to_date_param(d, 'to_creation_date')
        return d


class FilterLocksForm(AbstractFilterLocksForm):
    def __init__(self, *args, **kwargs):
        super(FilterLocksForm, self).__init__(*args, **kwargs)
        self.fields['user_id'] = forms.IntegerField(label=_('user id'),
            required=False)
        self.fields['balance_id'] = forms.IntegerField(label=_('balance id'),
            required=False)
        self._add_common_fields()


class FilterUserBalanceLocksForm(AbstractFilterLocksForm):
    def __init__(self, *args, **kwargs):
        super(FilterUserBalanceLocksForm, self).__init__(*args, **kwargs)
        self.fields['user_id'] = forms.IntegerField(label=_('user id'),
            widget=ConstInput, required=False)
        self.fields['balance_id'] = forms.IntegerField(label=_('balance id'),
            widget=ConstInput, required=False)
        self._add_common_fields()


class FilterSelfLocksForm(AbstractFilterLocksForm):
    action = 'get_locks_self'

    def __init__(self, *args, **kwargs):
        super(FilterSelfLocksForm, self).__init__(*args, **kwargs)
        self._add_common_fields()


class AbstractFilterTransactionsForm(FilterBillingForm):
    action = 'get_transactions'

    def _add_common_fields(self):
        self.fields['order_id'] = forms.CharField(label=_('order id'),
            max_length=64, required=False)
        self.fields['type'] = forms.ChoiceField(label=_('type'), required=False,
            widget=forms.widgets.RadioSelect(),
            choices=((None, _('all')), ('receipt', _('receipt')), ('bonus', _('bonus')),
                ('lock', _('lock')), ('unlock', _('unlock')), ('charge_off', _('charge off'))),
            initial='all')
        self.fields['from_creation_date'] = forms.DateField(label=_('from'), required=False)
        self.fields['to_creation_date'] = forms.DateField(label=_('to'), required=False)

    def as_helix_request(self):
        d = super(AbstractFilterLocksForm, self).as_helix_request()
        self._strip_filter_param(d, 'user_id')
        self._strip_filter_param(d, 'order_id')
        self._strip_filter_param(d, 'type')
        self._strip_filter_param(d, 'balance_id')
        self._strip_from_date_param(d, 'from_creation_date')
        self._strip_to_date_param(d, 'to_creation_date')

        return d


class FilterTransactionsForm(AbstractFilterTransactionsForm):
    def __init__(self, *args, **kwargs):
        super(FilterLocksForm, self).__init__(*args, **kwargs)
        self.fields['user_id'] = forms.IntegerField(label=_('user id'),
            required=False)
        self.fields['balance_id'] = forms.IntegerField(label=_('balance id'),
            required=False)
        self._add_common_fields()


class FilterUserTransactionsForm(AbstractFilterTransactionsForm):
    def __init__(self, *args, **kwargs):
        super(FilterUserBalanceLocksForm, self).__init__(*args, **kwargs)
        self.fields['user_id'] = forms.IntegerField(label=_('user id'),
            widget=ConstInput, required=False)
        self.fields['balance_id'] = forms.IntegerField(label=_('balance id'),
            widget=ConstInput, required=False)
        self._add_common_fields()


class FilterSelfLocksForm(AbstractFilterLocksForm):
    action = 'get_locks_self'

    def __init__(self, *args, **kwargs):
        super(FilterSelfLocksForm, self).__init__(*args, **kwargs)
        self._add_common_fields()