from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms import HelixwebRequestForm, _get_session_id
from helixweb.core.widgets import ConstInput


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

    @staticmethod
    def get_user_balance_req(request, balance_id):
        return {'action': 'get_balances', 'session_id': _get_session_id(request),
            'filter_params': {'id': int(balance_id)}, 'paging_params': {},
            'ordering_params': ['currency_id']}

    @staticmethod
    def get_balance_req(request, balance_id):
        return {'action': 'get_balances', 'session_id': _get_session_id(request),
            'filter_params': {'id': int(balance_id)}, 'paging_params':{}}

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
    locking_choices_sel_values = (0, 1, 2, 3)
    locking_choices_sel_names = ('only real', 'only virtual', 'real, virtual',
        'virtual, real')
    locking_choices_billing_values = (['real_amount'],
        ['virtual_amount'],
        ['real_amount', 'virtual_amount'],
        ['virtual_amount', 'real_amount'])

    @staticmethod
    def locking_choices():
        return zip(BalanceForm.locking_choices_sel_values,
            BalanceForm.locking_choices_sel_names)

    @staticmethod
    def locking_choice_by_locking_order(locking_order):
        result = None
        try:
            idx = BalanceForm.locking_choices_billing_values.index(locking_order)
            result = BalanceForm.locking_choices_sel_values[idx]
        except ValueError:
            pass
        return result

    @staticmethod
    def is_active_choices():
        return (('1', _('active')), ('0', _('inactive')))

    def _strip_locking_order(self, d, name='locking_order'):
        self._strip_param(d, name)
        if name in d:
            choice = int(d[name])
            choices = dict(zip(self.locking_choices_sel_values,
                self.locking_choices_billing_values))
            d[name] = choices[choice]

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
        user_id_widget = ConstInput if user_id else forms.widgets.TextInput
        self.fields['user_id'] = forms.IntegerField(label=_('user id'), initial=user_id,
            widget=user_id_widget)
        self.fields['currency_code'] = self._gen_currency_code(currencies)
        self.fields['overdraft_limit'] = forms.DecimalField(label=_('overdraft limit'),
            required=False)
        self.fields['locking_order'] = forms.ChoiceField(label=_('locking order'),
            required=False, choices=self.locking_choices(),
            widget=forms.widgets.RadioSelect)
        self.fields['is_active'] = forms.ChoiceField(label=_('is active'),
            widget=forms.widgets.RadioSelect(), initial='1',
            choices=self.is_active_choices())
        self.fields['check_user_exist'] = forms.ChoiceField(label=_('check user exist'),
            widget=forms.widgets.RadioSelect(), initial='1',
            choices=(('1', _('check')), ('0', _('not check'))))

    def as_helix_request(self):
        d = super(AddBalanceForm, self).as_helix_request()
        self._strip_param(d, 'user_id')
        self._strip_param(d, 'currency_code')
        self._strip_param(d, 'overdraft_limit')
        self._strip_bool_param(d, 'is_active')
        self._strip_bool_param(d, 'check_user_exist')
        return d


class ModifyBalanceForm(BalanceForm):
    action = 'modify_balances'

    def __init__(self, *args, **kwargs):
        super(ModifyBalanceForm, self).__init__(*args, **kwargs)

        self.fields['id'] = forms.IntegerField(label=_('id'),
            initial=kwargs.get('id'), widget=ConstInput)
        self.fields['user_id'] = forms.IntegerField(label=_('user id'),
            initial=kwargs.get('user_id'), widget=ConstInput)
        self.fields['currency_code'] = forms.CharField(label=_('currency_code'),
            initial=kwargs.get('currency_code'), widget=ConstInput)
        self.fields['new_overdraft_limit'] = forms.DecimalField(label=_('overdraft limit'),
            required=False)
        self.fields['new_locking_order'] = forms.ChoiceField(label=_('locking order'),
            required=False, choices=self.locking_choices(),
            widget=forms.widgets.RadioSelect)
        self.fields['new_is_active'] = forms.ChoiceField(label=_('is active'),
            widget=forms.widgets.RadioSelect(), choices=self.is_active_choices(),
            initial=kwargs.get('new_is_active'))

    @staticmethod
    def from_balance_info(balance_info, request):
        d = dict(balance_info)
        d['new_is_active'] = int(d['is_active'])
        d['new_overdraft_limit'] = d['overdraft_limit']
        new_lo_choice = ModifyBalanceForm.locking_choice_by_locking_order(
            d['locking_order'])
        d['new_locking_order'] = new_lo_choice
        return ModifyBalanceForm(d, request=request)

    def as_helix_request(self):
        d = super(ModifyBalanceForm, self).as_helix_request()
        d.pop('user_id')
        d.pop('currency_code')

        id = d.pop('id')
        d['ids'] = [id]
        self._strip_bool_param(d, 'new_is_active')
        self._strip_param(d, 'new_overdraft_limit')
        self._strip_locking_order(d, 'new_locking_order')

        return d


class AddMoneyForm(BillingForm):
    def __init__(self, *args, **kwargs):
        balance_id = kwargs.pop('balance_id')
        currency_code = kwargs.pop('currency_code')
        super(AddMoneyForm, self).__init__(*args, **kwargs)
        self.fields['balance_id'] = forms.IntegerField(label=_('balance id'), widget=ConstInput,
            initial=balance_id)
        self.fields['currency_code'] = forms.CharField(label=_('currency'), widget=ConstInput,
            initial=currency_code)
        self.fields['amount'] = forms.DecimalField(label=_('amount'))
        self.fields['description'] = forms.CharField(label=_('description'),
            widget=forms.widgets.Textarea({'rows': 3, 'cols': 20}), required=False)

    def as_helix_request(self):
        d = super(AddMoneyForm, self).as_helix_request()
        self._strip_param(d, 'balance_id')
        d.pop('currency_code')
        self._strip_param(d, 'amount')
        self._strip_param(d, 'description')
        info = {}
        if 'description' in d:
            info['description'] = d.pop('description')
        d['info'] = info
        return d


class AddReceiptForm(AddMoneyForm):
    action = 'add_receipt'


class AddBonusForm(AddMoneyForm):
    action = 'add_bonus'
