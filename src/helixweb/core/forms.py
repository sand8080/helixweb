from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList

from helixweb.core.client import Client
from django.utils.encoding import force_unicode


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
        url = kwargs.pop('service_url')
        self.action = kwargs.pop('action')
        self.session_id = kwargs.pop('session_id', None)
        self.c = Client(url)
#        super(HelixwebRequestForm, self).__init__(*args, **kwargs)
        super(HelixwebRequestForm, self).__init__(*args, error_class=ErrorFieldMaker, **kwargs)
        self.error_css_class = 'errormessage'

    def request(self, return_resp=False):
        d = dict(self.cleaned_data)
        d.pop('c', None)
        d['action'] = self.action
        d['custom_actor_info'] = __package__
        if self.session_id not in d and self.session_id is not None:
            d['session_id'] = self.session_id
        resp = self.c.request(d)
        self.process_errors(resp)
        return resp if return_resp else None

    def process_errors(self, resp):
        s = 'status'
        if s in resp and resp[s] == 'ok':
            return
        else:
            code = _(resp.get('code', None))
            fields = resp.get('fields', [])
            if not NON_FIELD_ERRORS in self._errors:
                self._errors[NON_FIELD_ERRORS] = self.error_class()
            self._errors[NON_FIELD_ERRORS].append(code)
            for f in fields:
                self._errors[f] = self.error_class()
                self._errors[f].append('')
            print filter(lambda x: x != NON_FIELD_ERRORS, self._errors.keys())

    def as_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            normal_row = u'<tr%(html_class_attr)s><th>%(label)s</th><td>%(field)s%(errors)s%(help_text)s</td></tr>',
            error_row = u'<tr><td colspan="2" style="text-align:center;">%s</td></tr>',
            row_ender = u'</td></tr>',
            help_text_html = u'<br />%s',
            errors_on_separate_row = False)
