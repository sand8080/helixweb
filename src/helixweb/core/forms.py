from django import forms
from django.forms.forms import NON_FIELD_ERRORS

from helixweb.core.client import Client


class HelixwebRequestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        url = kwargs.pop('service_url')
        self.action = kwargs.pop('action')
        self.session_id = kwargs.pop('session_id', None)
        self.c = Client(url)
        super(HelixwebRequestForm, self).__init__(*args, **kwargs)

    def request(self):
        d = dict(self.cleaned_data)
        d.pop('c', None)
        d['action'] = self.action
        d['custom_actor_info'] = __package__
        if self.session_id not in d and self.session_id is not None:
            d['session_id'] = self.session_id
        resp = self.c.request(d)
        self.process_errors(resp)

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

