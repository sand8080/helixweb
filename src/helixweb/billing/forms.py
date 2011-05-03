from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms import HelixwebRequestForm, _get_session_id


class BillingForm(HelixwebRequestForm):
    @staticmethod
    def get_currencies_req(request):
        return {'action': 'get_currencies',
            'session_id': _get_session_id(request)}

    @staticmethod
    def get_used_currencies_req(request):
        return {'action': 'get_used_currencies',
            'session_id': _get_session_id(request)}


class CurrenciesForm(BillingForm):
    action = 'get_currencies'
    ordering_params = ['-code']


class UsedCurrenciesForm(BillingForm):
    action = 'get_used_currencies'
    ordering_params = ['-code']


class ModifyUsedCurrenciesForm(BillingForm):
    action = 'modify_used_currencies'

    def __init__(self, *args, **kwargs):
        currencies = kwargs.pop('currencies', [])
        super(ModifyUsedCurrenciesForm, self).__init__(*args, **kwargs)
        choices = [(c['code'], '%s (%s)' % (c['code'], c['name'])) for c in currencies]
        self.fields['new_currencies_codes'] = forms.MultipleChoiceField(label=_('currencies'),
            required=False, choices=choices,
            widget=forms.widgets.CheckboxSelectMultiple)


class BalanceSelfForm(BillingForm):
    action = 'get_balance_self'
