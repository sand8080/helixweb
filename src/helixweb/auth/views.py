from datetime import datetime, timedelta
import base64

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf

from helixweb.auth import settings
from helixweb.auth.forms import LoginForm, AddServiceForm
from helixweb.core.localization import cur_lang, cur_lang_value
#from django.utils.translation import ugettext as _

from helixweb.core.client import Client
from helixweb.core.views import login_redirector


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


def _get_backurl(request):
    if 'backurl' in request.GET:
        return base64.decodestring(request.GET['backurl'])
    else:
        return '/%s/auth/services/' % cur_lang_value(request)


def login(request):
    c = {}
    c.update(csrf(request))
    c.update(cur_lang(request))
    if request.method == 'POST':
        form = LoginForm(request.POST, prefix='login')
        if form.is_valid():
            resp = form.request()
            status = resp.get('status', None)
            s_id = resp.get('session_id', None)
            if status == 'ok' and s_id is not None:
                # TODO: set secure cookie
                b_url = _get_backurl(request)
                response = HttpResponseRedirect(b_url)
                expires = datetime.strftime(datetime.utcnow() + timedelta(days=365), "%a, %d-%b-%Y %H:%M:%S GMT")
                response.set_cookie('session_id', value=s_id, expires=expires)
                return response
    else:
        form = LoginForm(prefix='login')
    c['login_form'] = form
    return render_to_response('login.html', c,
        context_instance=RequestContext(request))


def _get_services(request):
    cli = Client(settings.AUTH_SERVICE_URL)
    sess_id = _get_session_id(request)
    req = {'session_id': sess_id, 'action': 'get_services',
        'paging_params': {}, 'filter_params': {}}
    resp = cli.checked_request(req)
    if resp['status'] != 'ok':
        return {'services_error': resp['code']}
    else:
        return {'services': resp['services']}


@login_redirector
def services(request):
    c = _prepare_context(request)
    c.update(csrf(request))
    c.update(_get_services(request))
    if request.method == 'POST':
        form = AddServiceForm(request.POST, prefix='service',
            session_id=_get_session_id(request))
        if form.is_valid():
            resp = form.request()
            if resp.get('status', None) == 'ok':
                return HttpResponseRedirect('.')
    else:
        form = AddServiceForm(prefix='service')
    c['service_form'] = form
    return render_to_response('services.html', c,
        context_instance=RequestContext(request))
