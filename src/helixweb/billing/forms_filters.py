from django.utils.translation import ugettext_lazy as _

from helixweb.core.forms_filters import (FilterForm, AbstractFilterActionLogsForm,
    AbstractFilterAllActionLogsForm, AbstractFilterSelfActionLogsForm,
    AbstractFilterUserActionLogsForm)
from helixweb.core.forms import HelixwebRequestForm


class FilterBillingForm(FilterForm, HelixwebRequestForm):
    pass


class AbstractBillingFilterActionLogsForm(AbstractFilterActionLogsForm, FilterBillingForm):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = (
            ('', ''), ('modify_used_currencies', _('modify currencies')),
        )
        super(AbstractBillingFilterActionLogsForm, self).__init__(*args, **kwargs)


class FilterAllActionLogsForm(AbstractBillingFilterActionLogsForm, AbstractFilterAllActionLogsForm):
    pass


class FilterSelfActionLogsForm(AbstractBillingFilterActionLogsForm, AbstractFilterSelfActionLogsForm):
    pass


class FilterUserActionLogsForm(AbstractBillingFilterActionLogsForm, AbstractFilterUserActionLogsForm):
    pass