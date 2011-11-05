from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms import HelixwebRequestForm


class TariffForm(HelixwebRequestForm):
    pass


class AddTarifficationObjectForm(TariffForm):
    action = 'add_tariffication_object'
    name = forms.CharField(label=_('service name'), max_length=32)
