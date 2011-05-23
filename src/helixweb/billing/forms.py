from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms import HelixwebRequestForm, _get_session_id


class BillingForm(HelixwebRequestForm):
    @staticmethod
    def _simple_req(action, request):
        return {'action': action, 'session_id': _get_session_id(request)}

    @staticmethod
    def get_currencies_req(request):
        return BillingForm._simple_req('get_currencies', request)

    @staticmethod
    def get_used_currencies_req(request):
        return BillingForm._simple_req('get_used_currencies', request)

    @staticmethod
    def get_balances_self_req(request):
        return BillingForm._simple_req('get_balances_self', request)

    @staticmethod
    def get_user_balances_req(request, user_id):
        return {'action': 'get_balances', 'session_id': _get_session_id(request),
            'filter_params': {'user_id': int(user_id)}, 'paging_params': {},
            'ordering_params': ['currency_id']}

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


class BalanceForm(BillingForm):
    @staticmethod
    def locking_choices():
        return ((0, _('only real')), (1, _('only virtual')),
            (2, _('real, virtual')), (3, _('virtual, real')),)

    def _strip_locking_order(self, d):
        f_name = 'locking_order'
        self._strip_param(d, f_name)
        if f_name in d:
            choice = int(d[f_name])
            if choice == 0:
                d[f_name] = ['available_real_amount']
            elif choice == 1:
                d[f_name] = ['available_virtual_amount']
            elif choice == 3:
                d[f_name] = ['available_virtual_amount', 'available_virtual_amount']
            elif choice == 4:
                d[f_name] = ['available_virtual_amount', 'available_virtual_amount']

    def as_helix_request(self):
        d = super(BillingForm, self).as_helix_request()
        self._strip_locking_order(d)
        return d


class AddBalanceForm(BalanceForm):
    action = 'add_balance'

    def __init__(self, *args, **kwargs):
        currencies = kwargs.pop('currencies', [])
        user_id = kwargs.pop('user_id', None)
        super(AddBalanceForm, self).__init__(*args, **kwargs)
        user_id_widget = forms.widgets.HiddenInput if user_id else forms.widgets.TextInput
        self.fields['user_id'] = forms.IntegerField(label=_('user id'), initial=user_id,
            widget=user_id_widget)
        self.fields['currency_code'] = self._gen_currency_code(currencies)
        self.fields['overdraft_limit'] = forms.DecimalField(label=_('overdraft limit'),
            required=False)

        self.fields['locking_order'] = forms.ChoiceField(label=_('locking order'),
            required=False, choices=self.locking_choices(),
            widget=forms.widgets.RadioSelect, initial='None')

        self.fields['is_active'] = forms.ChoiceField(label=_('is active'),
            widget=forms.widgets.RadioSelect(), initial='1',
            choices=(('1', _('active')), ('0', _('inactive'))))
        self.fields['check_user_exist'] = forms.ChoiceField(label=_('check user exist'),
            widget=forms.widgets.RadioSelect(), initial='1',
            choices=(('1', _('check')), ('0', _('not check'))))

    def as_helix_request(self):
        d = super(AddBalanceForm, self).as_helix_request()
        self._strip_param(d, 'user_id')
        self._strip_param(d, 'currency_code')
        self._strip_param(d, 'overdraft_limit')
        d['is_active'] = bool(int(d['is_active']))
        d['check_user_exist'] = bool(int(d['check_user_exist']))
        return d
