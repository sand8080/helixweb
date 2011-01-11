from datetime import datetime, timedelta
import base64

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf

from helixweb.core.localization import cur_lang, cur_lang_value
#from django.utils.translation import ugettext as _
from helixweb.core.views import login_redirector, process_helix_response
from helixweb.core.client import Client
from helixweb.core.forms import _get_session_id

from helixweb.auth.forms import LoginForm, AddServiceForm, ModifyServiceForm,\
    ModifyEnvironmentForm, AddGroupForm, DeleteGroupForm, ModifyGroupForm
from helixweb.auth.forms_filters import FilterServiceForm, FilterGroupForm
from helixweb.auth.security import get_rights
from helixweb.auth import settings


helix_cli = Client(settings.AUTH_SERVICE_URL)


def _prepare_context(request):
    c = {}
    c['rights'] = get_rights(_get_session_id(request))
    c.update(csrf(request))
    c.update(cur_lang(request))
    return c


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
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.notchecked_request(form.as_helix_request())
            form.handle_errors(resp)
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
        form = LoginForm(request=request)
    c['login_form'] = form
    return render_to_response('login.html', c,
        context_instance=RequestContext(request))


@login_redirector
def add_service(request):
    c = _prepare_context(request)
    c.update(csrf(request))
    if request.method == 'POST':
        form = AddServiceForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') == '1':
                    return HttpResponseRedirect('.')
                else:
                    return HttpResponseRedirect('/auth/get_services/')
    else:
        form = AddServiceForm(request=request)
    c['add_service_form'] = form
    return render_to_response('service/add.html', c,
        context_instance=RequestContext(request))


@login_redirector
def modify_service(request, id):
    c = _prepare_context(request)
    c.update(csrf(request))
    if request.method == 'POST':
        form = ModifyServiceForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect('/auth/get_services/')
    else:
        resp = helix_cli.request(ModifyServiceForm.get_by_id_req(id, request))
        form = ModifyServiceForm.from_get_services_helix_resp(resp, request)
        if form.is_valid():
            form.handle_errors(resp)
    c['form'] = form
    return render_to_response('service/modify.html', c,
        context_instance=RequestContext(request))


@login_redirector
def services(request):
    c = _prepare_context(request)
    c.update(csrf(request))

    if len(request.GET) == 0 or (len(request.GET) == 1 and 'pager_offset' in request.GET):
        # setting default is_active value to True
        form = FilterServiceForm({'is_active': 'all'}, request=request)
    else:
        form = FilterServiceForm(request.GET, request=request)

    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        form.update_total(resp)
        c.update(process_helix_response(resp, 'services', 'services_error'))
        c['pager'] = form.pager

    c['filter_service_form'] = form

    return render_to_response('service/list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def modify_environment(request):
    c = _prepare_context(request)
    c.update(csrf(request))

    if request.method == 'POST':
        form = ModifyEnvironmentForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
    else:
        resp = helix_cli.request(ModifyEnvironmentForm.get_req(request))
        form = ModifyEnvironmentForm.from_get_helix_resp(resp, request)
        if form.is_valid():
            form.handle_errors(resp)
    c['modify_environment_form'] = form

    return render_to_response('environment/modify.html', c,
        context_instance=RequestContext(request))


@login_redirector
def groups(request):
    c = _prepare_context(request)
    c.update(csrf(request))

    resp = helix_cli.request(FilterGroupForm.get_services_req(request))
    srvs = resp.get('services', [])
    srvs_idx = {}
    for s in srvs:
        srvs_idx[s['id']] = s
    c['services_idx'] = srvs_idx

    if len(request.GET) == 0 or (len(request.GET) == 1 and 'pager_offset' in request.GET):
        # setting default is_active value to True
        form = FilterGroupForm({'is_active': 'all'}, request=request)
    else:
        form = FilterGroupForm(request.GET, request=request)

    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        form.update_total(resp)
        c.update(process_helix_response(resp, 'groups', 'groups_error'))
        c['pager'] = form.pager

    c['filter_group_form'] = form

    return render_to_response('group/list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def add_group(request):
    c = _prepare_context(request)
    c.update(csrf(request))
    resp = helix_cli.request(AddGroupForm.get_services_req(request))
    services = resp.get('services', [])
    c.update(process_helix_response(resp, 'services', 'services_error'))

    if request.method == 'POST':
        form = AddGroupForm(request.POST, services=services, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect('../get_groups/')
                else:
                    return HttpResponseRedirect('')
    else:
        form = AddGroupForm(services=services, request=request)

    c['add_group_form'] = form
    return render_to_response('group/add.html', c,
        context_instance=RequestContext(request))


@login_redirector
def delete_group(request, id):
    c = _prepare_context(request)
    c.update(csrf(request))
    if request.method == 'POST':
        form = DeleteGroupForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                return HttpResponseRedirect('/auth/get_groups/')
    else:
        resp = helix_cli.request(DeleteGroupForm.get_by_id_req(id, request))
        groups = resp.get('groups', [{}])
        d_grp = groups[0] if len(groups) else {}
        form = DeleteGroupForm(d_grp, request=request)
        if form.is_valid():
            form.handle_errors(resp)

    c['form'] = form
    return render_to_response('group/delete.html', c,
        context_instance=RequestContext(request))


@login_redirector
def modify_group(request, id):
    c = _prepare_context(request)
    c.update(csrf(request))
    resp = helix_cli.request(ModifyGroupForm.get_services_req(request))
    services = resp.get('services', [])
    c.update(process_helix_response(resp, 'services', 'services_error'))

    if request.method == 'POST':
        form = ModifyGroupForm(request.POST, services=services, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect('/auth/get_groups/')
    else:
        resp = helix_cli.request(ModifyGroupForm.get_by_id_req(id, request))
        form = ModifyGroupForm.from_get_groups_helix_resp(resp, request, services)
        if form.is_valid():
            form.handle_errors(resp)
    c['form'] = form
    return render_to_response('group/modify.html', c,
        context_instance=RequestContext(request))
