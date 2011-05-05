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

    def _gen_currency_code(self, currencies, required=True):
        choices = [(None, '--')] + [(c['code'], c['code']) for c in currencies]
        return forms.ChoiceField(label=_('currency'), choices=choices,
            widget=forms.widgets.Select, required=required)


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


class AddBalanceForm(BillingForm):
    action = 'add_balance'

    def __init__(self, *args, **kwargs):
        currencies = kwargs.pop('currencies', [])
        super(AddBalanceForm, self).__init__(*args, **kwargs)
        self.fields['user_id'] = forms.CharField(label=_('user id'), max_length=32)
        self.fields['currency_code'] = self._gen_currency_code(currencies)
        self.fields['overdraft_limit'] = forms.DecimalField(label=_('overdraft limit'),
            required=False)
        # TODO: implement locking order
#        locking_choices = [('available_real_amount', 'real'),
#            ('available_virtual_amount', 'virtual')]
#        self.fields['locking_order'] = forms.MultipleChoiceField(label=_('locking order'),
#            required=False, choices=locking_choices,
#            widget=forms.widgets.CheckboxSelectMultiple)
        self.fields['is_active'] = forms.ChoiceField(label=_('is active'),
            widget=forms.widgets.RadioSelect(), initial='1',
            choices=(('1', _('active')), ('0', _('inactive'))))

    def as_helix_request(self):
        d = super(AddBalanceForm, self).as_helix_request()
        self._strip_param(d, 'user_id')
        self._strip_param(d, 'currency_code')
        self._strip_param(d, 'overdraft_limit')
        d['is_active'] = bool(int(d['is_active']))
        return d
