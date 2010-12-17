from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList

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
        request = kwargs.pop('request')
        self.session_id = request.COOKIES.get('session_id', None)
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
#            print filter(lambda x: x != NON_FIELD_ERRORS, self._errors.keys())

    def as_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            normal_row = u'<tr%(html_class_attr)s><th>%(label)s</th><td>%(field)s%(errors)s%(help_text)s</td></tr>',
            error_row = u'<tr><td colspan="2" style="text-align:center;">%s</td></tr>',
            row_ender = u'</td></tr>',
            help_text_html = u'<br />%s',
            errors_on_separate_row = False)
