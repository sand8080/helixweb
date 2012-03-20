import datetime
import pytz

from django import forms
from django.utils.translation import ugettext_lazy as _

from helixweb.core.pager import Pager


class FilterForm(object):
    def __init__(self, *args, **kwargs):
        self.pager = self._get_pager(kwargs['request'])
        super(FilterForm, self).__init__(*args, **kwargs)

    def _get_pager(self, request):
        on_page = request.COOKIES.get('pager_on_page', 0)
        total = request.GET.get('pager_total', None)
        offset = request.GET.get('pager_offset', 0)
        return Pager(offset, total, on_page)

    def as_helix_request(self):
        f_params = dict(self.cleaned_data)
        d = super(FilterForm, self).as_helix_request()
        for k in f_params.keys():
            del d[k]
        d['filter_params'] = f_params
        d['paging_params'] = {'limit': self.pager.on_page,
            'offset': self.pager.offset}

        if hasattr(self, 'ordering_param'):
            d['ordering_params'] = [self.ordering_param]
        elif hasattr(self, 'ordering_params'):
            d['ordering_params'] = self.ordering_params
        else:
            d['ordering_params'] = ['-id']

        return d

    def update_total(self, helix_resp):
        self.pager.update_total(helix_resp)

    def _strip_filter_param(self, d, name, new_name=None):
        self._strip_param(d['filter_params'], name, new_name)

    def _strip_from_date_param(self, d, name):
        self._strip_filter_param(d, name)
        f_params = d['filter_params']
        f_d = f_params.get(name, None)
        if f_d:
            res_f_d = datetime.datetime(year=f_d.year,
                month=f_d.month, day=f_d.day, hour=0, minute=0,
                second=0, tzinfo=pytz.utc)
            f_params[name] = res_f_d.isoformat()

    def _strip_to_date_param(self, d, name):
        self._strip_filter_param(d, name)
        f_params = d['filter_params']
        f_d = f_params.get(name, None)
        if f_d:
            res_f_d = datetime.datetime(year=f_d.year,
                month=f_d.month, day=f_d.day, hour=23, minute=59,
                second=59, tzinfo=pytz.utc)
            f_params[name] = res_f_d.isoformat()


class AbstractFilterActionLogsForm(object):
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        super(AbstractFilterActionLogsForm, self).__init__(*args, **kwargs)

        action_name = forms.CharField(label=_('action name'), required=False,
            widget=forms.widgets.Select(choices=choices))
        user_id = forms.IntegerField(label=_('user id'), required=False)
        sess_id = forms.CharField(label=_('session'), max_length=40,
            required=False)
        from_request_date = forms.DateField(label=_('from'), required=False)
        to_request_date = forms.DateField(label=_('to'), required=False)

        self.fields['action_name'] = action_name
        self.fields['user_id'] = user_id
        self.fields['sess_id'] = sess_id
        self.fields['from_request_date'] = from_request_date
        self.fields['to_request_date'] = to_request_date

    def as_helix_request(self):
        d = super(AbstractFilterActionLogsForm, self).as_helix_request()
        self._strip_filter_param(d, 'action_name', new_name='action')
        self._strip_filter_param(d, 'sess_id', new_name='session_id')
        self._strip_from_date_param(d, 'from_request_date')
        self._strip_to_date_param(d, 'to_request_date')
        self._strip_filter_param(d, 'user_id')
        return d


class AbstractFilterAllActionLogsForm(AbstractFilterActionLogsForm):
    def __init__(self, *args, **kwargs):
        self.action = 'get_action_logs'
        super(AbstractFilterAllActionLogsForm, self).__init__(*args, **kwargs)


class AbstractFilterSelfActionLogsForm(AbstractFilterActionLogsForm):
    def __init__(self, *args, **kwargs):
        self.action = 'get_action_logs_self'
        super(AbstractFilterSelfActionLogsForm, self).__init__(*args, **kwargs)


class AbstractFilterUserActionLogsForm(AbstractFilterActionLogsForm):
    def __init__(self, *args, **kwargs):
        self.action = 'get_action_logs'
        self.user_id = int(kwargs.pop('id'))
        super(AbstractFilterUserActionLogsForm, self).__init__(*args, **kwargs)
        del self.fields['user_id']

    def as_helix_request(self):
        d = super(AbstractFilterUserActionLogsForm, self).as_helix_request()
        d['filter_params']['user_id'] = self.user_id
        return d
