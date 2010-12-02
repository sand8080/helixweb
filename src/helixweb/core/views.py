import base64

from helixweb.error import UnauthorizedActivity
from django.http import HttpResponseRedirect


def login_redirector(func):
    def decorated(request):
        try:
            return func(request)
        except UnauthorizedActivity:
            b_url = base64.encodestring(request.get_full_path())
            return HttpResponseRedirect('/auth/login/?backurl=%s' % b_url)
    return decorated


