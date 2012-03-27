from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms_filters import (FilterForm, AbstractFilterActionLogsForm,
    AbstractFilterAllActionLogsForm, AbstractFilterSelfActionLogsForm,
    AbstractFilterUserActionLogsForm)
from helixweb.tariff.forms import TariffForm


class FilterTariffForm(FilterForm, TariffForm):
    pass


class AbstractTariffFilterActionLogsForm(AbstractFilterActionLogsForm, FilterTariffForm):
    action = 'get_action_logs'
    def __init__(self, *args, **kwargs):
        # TODO: add all actions
        kwargs['choices'] = (('', ''),
            ('add_tariffication_object', _('add tariffication object')),
        )
        super(AbstractTariffFilterActionLogsForm, self).__init__(*args, **kwargs)


class FilterAllActionLogsForm(AbstractTariffFilterActionLogsForm, AbstractFilterAllActionLogsForm):
    pass


class FilterSelfActionLogsForm(AbstractTariffFilterActionLogsForm, AbstractFilterSelfActionLogsForm):
    pass


class FilterUserActionLogsForm(AbstractTariffFilterActionLogsForm, AbstractFilterUserActionLogsForm):
    pass


class FilterTarifficationObjectsForm(FilterTariffForm):
    action = 'get_tariffication_objects'
    id = forms.IntegerField(label=_('tariffication object id'), required=False)
    name = forms.CharField(label=_('tariffication object name'), max_length=32,
        required=False)

    def as_helix_request(self):
        d = super(FilterTarifficationObjectsForm, self).as_helix_request()
        self._strip_filter_param(d, 'id')
        self._strip_filter_param(d, 'name')
        return d


class FilterTariffsForm(FilterTariffForm):
    action = 'get_tariffs'
#    name = forms.CharField(label=_('tariff name'), max_length=32,
#        required=False)

    def as_helix_request(self):
        d = super(FilterTariffsForm, self).as_helix_request()
#        self._strip_filter_param(d, 'name')
        return d
