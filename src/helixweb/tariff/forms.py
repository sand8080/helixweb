from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms import HelixwebRequestForm
from helixweb.core.context_processors import _get_session_id
from helixweb.core.widgets import ConstInput


class TariffForm(HelixwebRequestForm):
    @staticmethod
    def get_tariffication_object_req(request, to_id):
        return {'action': 'get_tariffication_objects', 'session_id': _get_session_id(request),
            'filter_params': {'ids': [int(to_id)]}, 'paging_params':{}}


class AddTarifficationObjectForm(TariffForm):
    action = 'add_tariffication_object'
    name = forms.CharField(label=_('service name'), max_length=32)


class ModifyTarifficationObjectForm(TariffForm):
    action = 'modify_tariffication_object'
    id = forms.IntegerField(label=_('id'), widget=ConstInput)
    new_name = forms.CharField(label=_('name'), max_length=32)

    @staticmethod
    def from_get_helix_resp(helix_resp, request):
        tos = helix_resp['tariffication_objects']
        if len(tos) == 1:
            to_info = dict(tos[0])
            to_info['new_name'] = to_info['name']
            to_info.pop('name')
        else:
            to_info = {}
        return ModifyTarifficationObjectForm(to_info, request=request)
