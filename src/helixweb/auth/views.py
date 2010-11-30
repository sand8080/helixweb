from datetime import datetime, timedelta

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf

from helixweb.auth import settings
from helixweb.auth.forms import LoginForm
from helixweb.core.localization import cur_lang, cur_lang_value
#from django.utils.translation import ugettext as _

from helixweb.core.client import Client


def _prepare_context(request):
    c = {}
    c.update(csrf(request))
    c.update(cur_lang(request))
    return c


def _handle_not_logged(request):
    if 'session_id' not in request.COOKIES:
        return HttpResponseRedirect('/%s/auth/login/' % cur_lang_value(request))


def _get_session_id(request):
    return request.COOKIES.get('session_id', '')


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


def services(request):
    c = _prepare_context(request)
    cli = Client(settings.AUTH_SERVICE_URL)
    req = {'session_id': _get_session_id(request),
        'action': 'get_services', 'paging_params': {}, 'filter_params': {}}
    resp = cli.request(req)
    print resp
    return render_to_response('services.html', c,
        context_instance=RequestContext(request))

