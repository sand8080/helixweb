from datetime import datetime, timedelta

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf

from helixweb.auth.forms import LoginForm
from helixweb.core.localization import cur_lang
#from django.utils.translation import ugettext as _

def login(request):
    c = {}
    c.update(csrf(request))
    cl_dict = cur_lang(request)
    cl = cl_dict['cur_lang']
    c.update(cl_dict)
    if request.method == 'POST':
        form = LoginForm(request.POST, prefix='login')
        if form.is_valid():
            resp = form.request(return_resp=True)
            status = resp.get('status', None)
            s_id = resp.get('session_id', None)
            if status == 'ok' and s_id is not None:
                # TODO: set secure cookie
                response = HttpResponseRedirect('/%s/auth/login/' % cl)
                expires = datetime.strftime(datetime.utcnow() + timedelta(days=365), "%a, %d-%b-%Y %H:%M:%S GMT")
                response.set_cookie('session_id', value=s_id, expires=expires)
                return response
    else:
        form = LoginForm(prefix='login')
    c['login_form'] = form
    return render_to_response('login.html', c,
        context_instance=RequestContext(request))
