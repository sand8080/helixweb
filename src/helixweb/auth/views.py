from datetime import datetime, timedelta
import base64

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf

from helixweb.core.localization import cur_lang, cur_lang_value
#from django.utils.translation import ugettext as _
from helixweb.core.client import Client
from helixweb.core.views import login_redirector

from helixweb.auth import settings
from helixweb.auth.forms import LoginForm, AddServiceForm
from helixweb.auth.forms_filters import FilterServiceForm


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
            resp = form.notchecked_request()
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


def _process_response(resp, f_name, f_err_name):
    if resp['status'] != 'ok':
        return {f_err_name: resp['code']}
    else:
        return {f_name: resp[f_name]}


@login_redirector
def add_service(request):
    c = _prepare_context(request)
    c.update(csrf(request))
    add_fp = 'add_service'
    if request.method == 'POST':
        add_form = AddServiceForm(request.POST, prefix=add_fp,
            session_id=_get_session_id(request))
        if add_form.is_valid():
            resp = add_form.request()
            if resp.get('status', None) == 'ok':
                print '####', request.POST
                if request.POST.get('stay_here', '0') == '1':
                    print 'Stay here'
                    return HttpResponseRedirect('.')
                else:
                    print 'Go to services'
                    return HttpResponseRedirect('..')

    else:
        add_form = AddServiceForm(prefix=add_fp)

    c['add_service_form'] = add_form

    return render_to_response('services/add.html', c,
        context_instance=RequestContext(request))


@login_redirector
def services(request):
    c = _prepare_context(request)
    c.update(csrf(request))

    filter_fp = 'filter_services'

    if request.method == 'GET' and len(request.GET):
        filter_form = FilterServiceForm(request.GET, prefix=filter_fp,
            session_id=_get_session_id(request))
    else:
        filter_form = FilterServiceForm({'%s-is_active' % filter_fp: True},
            prefix=filter_fp, session_id=_get_session_id(request))

    if filter_form.is_valid():
        resp = filter_form.request()
        c.update(_process_response(resp, 'services', 'services_error'))

    c['filter_service_form'] = filter_form

    return render_to_response('services/list.html', c,
        context_instance=RequestContext(request))
