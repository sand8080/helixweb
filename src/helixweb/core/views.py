import base64

from helixweb.error import UnauthorizedActivity
from django.http import HttpResponseRedirect


def login_redirector(func):
    def decorated(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except UnauthorizedActivity:
            b_url = base64.encodestring(request.get_full_path())
            return HttpResponseRedirect('/auth/login/?backurl=%s' % b_url)
    return decorated


def process_helix_response(resp, f_name, f_err_name):
    if resp['status'] != 'ok':
        return {f_err_name: resp['code']}
    else:
        return {f_name: resp[f_name]}
