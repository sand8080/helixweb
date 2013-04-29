from decimal import Decimal

from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList
from django.utils.encoding import force_unicode

from helixweb.core.context_processors import _get_session_id


class ErrorFieldMaker(ErrorList):
    """
    A collection of errors that knows how to display itself in various formats.
    """
    def __unicode__(self):
        return self.as_text()

    def as_text(self):
        if not self:
            return u''
        msg = ', '.join([u'%s' % force_unicode(e) for e in self])
        return u'<span class="errormessage">* %s</span>' % msg


class HelixwebRequestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        self.session_id = _get_session_id(request)
        super(HelixwebRequestForm, self).__init__(*args, error_class=ErrorFieldMaker, **kwargs)
        self.error_css_class = 'errormessage'

    def as_helix_request(self):
        d = dict(self.cleaned_data)
        d['action'] = self.action
        d['custom_actor_info'] = __package__
        if self.session_id not in d and self.session_id is not None:
            d['session_id'] = self.session_id
        return d

    def handle_errors(self, resp):
        s = 'status'
        if s in resp and resp[s] == 'ok':
            return
        else:
            code = _(resp.get('code', None))
            fields = resp.get('fields', [])
            if NON_FIELD_ERRORS not in self._errors:
                self._errors[NON_FIELD_ERRORS] = self.error_class()
            self._errors[NON_FIELD_ERRORS].append(code)
            for f in fields:
                self._errors[f] = self.error_class()
                self._errors[f].append('')

    def as_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            normal_row = u'<tr%(html_class_attr)s><th>%(label)s</th><td>%(field)s%(errors)s%(help_text)s</td></tr>',
            error_row = u'<tr><td colspan="2" style="text-align:center;">%s</td></tr>',
            row_ender = u'</td></tr>',
            help_text_html = u'<br />%s',
            errors_on_separate_row = False)

    @staticmethod
    def get_services_req(request):
        return {'action': 'get_services', 'session_id': _get_session_id(request),
            'filter_params': {}, 'paging_params': {}}

    @staticmethod
    def get_active_groups_req(request):
        return {'action': 'get_groups', 'session_id': _get_session_id(request),
            'filter_params': {'is_active': True}, 'paging_params': {}}

    @staticmethod
    def get_users_req(request, ids):
        return {'action': 'get_users', 'session_id': _get_session_id(request),
            'filter_params': {'ids': ids}, 'paging_params': {}}

    @staticmethod
    def get_user_req(request):
        return {'action': 'get_user_self', 'session_id': _get_session_id(request)}

    def _strip_param(self, d, name, new_name=None):
        if new_name is None:
            new_name = name
        if name in d:
            p = d.pop(name, None)
            if isinstance(p, (str, unicode)):
                p = p.strip()
                if p == 'None':
                    p = None
            elif isinstance(p, Decimal):
                p = '%s' % p
            if p:
                d[new_name] = p

    def _strip_bool_param(self, d, name, new_name=None):
        if new_name is None:
            new_name = name
        self._strip_param(d, name, new_name=new_name)
        if new_name in d:
            d[new_name] = bool(int(d[new_name]))

    def _strip_int_param(self, d, name, new_name=None):
        if new_name is None:
            new_name = name
        self._strip_param(d, name, new_name=new_name)
        if new_name in d:
            d[new_name] = int(d[new_name])
