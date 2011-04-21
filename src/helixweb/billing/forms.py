from helixweb.core.forms import HelixwebRequestForm


class CurrenciesForm(HelixwebRequestForm):
    action = 'get_currencies'
    ordering_params = ['-code']


class UsedCurrenciesForm(HelixwebRequestForm):
    action = 'get_used_currencies'
    ordering_params = ['-code']
