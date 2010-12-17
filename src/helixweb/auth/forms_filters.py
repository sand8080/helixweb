from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms_filters import FilterForm
from helixweb.core.forms import HelixwebRequestForm


class FilterAuthForm(FilterForm, HelixwebRequestForm):
    pass


class FilterServiceForm(FilterAuthForm):
    type = forms.CharField(label=_('service type'), max_length=32,
        required=False)
    is_active = forms.BooleanField(label=_('is active'), required=False)

    def __init__(self, *args, **kwargs):
        self.action = 'get_services'
        super(FilterServiceForm, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        d = super(FilterServiceForm, self).as_helix_request()
        s_t = d['filter_params'].pop('type').strip()
        if len(s_t):
            d['filter_params']['type'] = s_t
        return d
