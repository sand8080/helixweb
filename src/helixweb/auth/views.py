from datetime import datetime, timedelta
import base64

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf

from helixweb.core.localization import cur_lang, cur_lang_value
#from django.utils.translation import ugettext as _
from helixweb.core.views import login_redirector

from helixweb.auth.forms import LoginForm, AddServiceForm
from helixweb.auth.forms_filters import FilterServiceForm
from helixweb.auth.security import get_rights


def _prepare_context(request):
    c = {}
    c['rights'] = get_rights(request.COOKIES.get('session_id', ''))
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
        return '/%s/auth/get_services/' % cur_lang_value(request)


def login(request):
    c = {}
    c.update(csrf(request))
    c.update(cur_lang(request))
    if request.method == 'POST':
        form = LoginForm(request.POST, prefix='login', request=request)
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
        form = LoginForm(prefix='login', request=request)
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
            request=request)
        if add_form.is_valid():
            resp = add_form.request()
            if resp.get('status', None) == 'ok':
                if request.POST.get('stay_here', '0') == '1':
                    return HttpResponseRedirect('.')
                else:
                    return HttpResponseRedirect('../get_services/')
    else:
        add_form = AddServiceForm(prefix=add_fp, request=request)

    c['add_service_form'] = add_form

    return render_to_response('services/add.html', c,
        context_instance=RequestContext(request))


@login_redirector
def services(request):
    c = _prepare_context(request)
    c.update(csrf(request))

    f_prefix = 'filter_services'

    if request.method == 'GET' and len(request.GET):
        form = FilterServiceForm(request.GET, prefix=f_prefix, request=request)
    else:
        # setting default is_active value to True
        form = FilterServiceForm({'%s-is_active' % f_prefix: True},
            prefix=f_prefix, request=request)

    if form.is_valid():
        resp = form.request()
        c.update(_process_response(resp, 'services', 'services_error'))
        c['pager'] = form.pager

    c['filter_service_form'] = form

    return render_to_response('services/list.html', c,
        context_instance=RequestContext(request))
