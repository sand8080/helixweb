from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms import HelixwebRequestForm, _get_session_id
from helixweb.auth.widgets import ServicesSelectMultiple, ConstInput


class CurrenciesForm(HelixwebRequestForm):
    action = 'get_currencies'

    ordering_params = ['-code']
#    @classmethod
#    def get_req(cls, request):
#        return {'action': cls.action,
#            'session_id': _get_session_id(request)}
