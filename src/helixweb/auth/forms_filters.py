from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.auth.forms import AuthForm
from helixweb.core.forms_filters import FilterForm


class FilterAuthForm(FilterForm, AuthForm):
    pass


class FilterServiceForm(FilterAuthForm):
    type = forms.CharField(label=_('service type'), max_length=32,
        required=False)
    is_active = forms.BooleanField(label=_('is active'), required=False)

    def __init__(self, *args, **kwargs):
        kwargs['action'] = 'get_services'
        super(FilterServiceForm, self).__init__(*args, **kwargs)

    def _get_cleaned_data(self):
        d = super(FilterServiceForm, self)._get_cleaned_data()
        s_t = d['filter_params'].pop('type').strip()
        if len(s_t):
            d['filter_params']['type'] = s_t
        return d
