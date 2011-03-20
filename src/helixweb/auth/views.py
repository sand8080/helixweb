from datetime import datetime, timedelta
import base64
import iso8601
import cjson

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf

from helixweb.core.localization import cur_lang, cur_lang_value
#from django.utils.translation import ugettext as _
from helixweb.core.views import login_redirector, process_helix_response
from helixweb.core.client import Client
from helixweb.core.forms import _get_session_id

from helixweb.auth.forms import (LoginForm, AddServiceForm, ModifyServiceForm,
    ModifyEnvironmentForm, AddGroupForm, DeleteGroupForm, ModifyGroupForm,
    ModifyUserSelfForm, AddUserForm, GroupForm, LogoutForm, AddEnvironmentForm,
    ModifyUsersForm)
from helixweb.auth.forms_filters import (FilterServiceForm, FilterGroupForm,
    FilterUserForm, FilterActionLogsForm, FilterActionLogsSelfForm)
from helixweb.auth.security import get_rights
from helixweb.auth import settings


helix_cli = Client(settings.AUTH_SERVICE_URL)


def _prepare_context(request):
    c = {}
    c['rights'] = get_rights(_get_session_id(request))
    c['logged_in'] = True
    c['cur_service'] = 'auth'
    c.update(cur_lang(request))
    c.update(csrf(request))
    return c


def _get_backurl(request):
    default_url = '/%s/auth/' % cur_lang_value(request)
    if 'backurl' in request.GET:
        try:
            return base64.decodestring(request.GET['backurl'])
        except Exception:
            return default_url
    else:
        return default_url


def _build_index(helix_resp, field):
    ds = helix_resp.get(field, [])
    ds_idx = {}
    for d in ds:
        ds_idx[d['id']] = d
    return ds_idx


def _make_login(form, request):
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
    return None


def login(request):
    c = {}
    c.update(csrf(request))
    c.update(cur_lang(request))
    if request.method == 'POST':
        form = LoginForm(request.POST, request=request)
        response = _make_login(form, request)
        if response:
            return response
    else:
        form = LoginForm(request=request)
    c['form'] = form
    return render_to_response('login.html', c,
        context_instance=RequestContext(request))


@login_redirector
def logout(request):
    form = LogoutForm({}, request=request)
    if form.is_valid():
        helix_cli.request(form.as_helix_request())
    resp = HttpResponseRedirect('/auth/login/')
    resp.delete_cookie('session_id')
    return resp


@login_redirector
def description(request):
    c = _prepare_context(request)
    return render_to_response('description.html', c,
        context_instance=RequestContext(request))


@login_redirector
def add_service(request):
    c = _prepare_context(request)
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
    c['form'] = form
    return render_to_response('service/add.html', c,
        context_instance=RequestContext(request))


@login_redirector
def modify_service(request, id):
    c = _prepare_context(request)
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


def add_environment(request):
    c = {}
    c.update(csrf(request))
    c.update(cur_lang(request))
    if request.method == 'POST':
        form = AddEnvironmentForm(request.POST, request=request)
        response = _make_login(form, request)
        if response:
            return response
    else:
        form = AddEnvironmentForm(request=request)
    c['form'] = form
    return render_to_response('environment/add.html', c,
        context_instance=RequestContext(request))


@login_redirector
def modify_environment(request):
    c = _prepare_context(request)
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
def add_user(request):
    c = _prepare_context(request)
    resp = helix_cli.request(GroupForm.get_active_groups_req(request))
    c.update(process_helix_response(resp, 'groups', 'groups_error'))
    groups = resp.get('groups', [])
    if request.method == 'POST':
        form = AddUserForm(request.POST, groups=groups, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') == '1':
                    return HttpResponseRedirect('.')
                else:
                    return HttpResponseRedirect('/auth/get_users/')
    else:
        form = AddUserForm(groups=groups, request=request)
    c['form'] = form
    return render_to_response('user/add.html', c,
        context_instance=RequestContext(request))


def _merge_groups_rights(groups_idx, groups_ids):
    result = []
    for g_id in groups_ids:
        group = groups_idx[g_id]
        rights = group['rights']
        for r in rights:
            if result:
                pass
            else:
                result[r]
    return result


@login_redirector
def users(request):
    c = _prepare_context(request)
    resp = helix_cli.request(FilterUserForm.get_active_groups_req(request))
    c.update(process_helix_response(resp, 'groups', 'groups_error'))
    groups_idx = _build_index(resp, 'groups')
    c['groups_idx'] = groups_idx

    resp = helix_cli.request(FilterUserForm.get_services_req(request))
    c.update(process_helix_response(resp, 'services', 'services_error'))
    c['services_idx'] = _build_index(resp, 'services')

    if len(request.GET) == 0 or (len(request.GET) == 1 and 'pager_offset' in request.GET):
        # setting default is_active value to True
        form = FilterUserForm({'is_active': 'all'}, request=request)
    else:
        form = FilterUserForm(request.GET, request=request)

    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        form.update_total(resp)
        users_list = resp.get('users', [])
        _calculate_summary_user_rights(users_list, groups_idx)
        c.update(process_helix_response(resp, 'users', 'users_error'))
        c['pager'] = form.pager
    c['form'] = form
    return render_to_response('user/list.html', c,
        context_instance=RequestContext(request))


def _calculate_summary_user_rights(users, groups_idx):
    def _get_summary_service(rights, srv_id):
        for r in rights:
            if r['service_id'] == srv_id:
                return r
        return None

    for u in users:
        rights = []
        for grp_id in u['groups_ids']:
            if grp_id not in groups_idx:
                continue
            grp = groups_idx[grp_id]
            grp_rights = grp['rights']
            for srv in grp_rights:
                srv_id = srv['service_id']
                summ_rights = _get_summary_service(rights, srv_id)
                if summ_rights is None:
                    rights.append(srv)
                else:
                    summ_rights['properties'] += srv['properties']
        u['rights'] = rights


@login_redirector
def modify_user_self(request):
    c = _prepare_context(request)
    if request.method == 'POST':
        form = ModifyUserSelfForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
    else:
        form = ModifyUserSelfForm(request=request)
    c['form'] = form
    return render_to_response('user/modify_user_self.html', c,
        context_instance=RequestContext(request))


@login_redirector
def modify_users(request, id):
    c = _prepare_context(request)
    if request.method == 'POST':
        form = ModifyUsersForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
    else:
        resp = helix_cli.request(ModifyUsersForm.get_users_req(id, request))
        c.update(process_helix_response(resp, 'users', 'users_error'))
        form = ModifyUsersForm(request=request)
        if 'users' in resp:
            if len(resp['users']) != 1:
                c['users_error'] = 'HELIXAUTH_USER_ACCESS_DENIED'
            else:
                form = ModifyUsersForm.from_get_helix_resp(resp, request)
    c['form'] = form
    return render_to_response('user/modify_users.html', c,
        context_instance=RequestContext(request))


@login_redirector
def groups(request):
    c = _prepare_context(request)
    resp = helix_cli.request(FilterGroupForm.get_services_req(request))
    c.update(process_helix_response(resp, 'services', 'services_error'))
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

    c['form'] = form

    return render_to_response('group/list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def add_group(request):
    c = _prepare_context(request)
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
    resp = helix_cli.request(ModifyGroupForm.get_services_req(request))
    c.update(process_helix_response(resp, 'services', 'services_error'))
    services = resp.get('services', [])

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


def _prepare_action_log(a_log):
    a_log['request_date'] = iso8601.parse_date(a_log['request_date'])
    a_log['request'] = cjson.decode(a_log['request'])
    a_log['response'] = cjson.decode(a_log['response'])
    return a_log


def _action_logs(request, al_form_cls):
    c = _prepare_context(request)
    if request.method == 'GET':
        form = al_form_cls(request.GET, request=request)
    else:
        form = al_form_cls({}, request=request)
    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        form.update_total(resp)
        if 'action_logs' in resp:
            resp['action_logs'] = map(_prepare_action_log, resp['action_logs'])
        c.update(process_helix_response(resp, 'action_logs', 'action_logs_error'))
        c['pager'] = form.pager
    c['form'] = form
    return c


@login_redirector
def action_logs(request):
    c = _action_logs(request, FilterActionLogsForm)
    return render_to_response('action_logs/list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def action_logs_self(request):
    c = _action_logs(request, FilterActionLogsSelfForm)
    return render_to_response('action_logs/list.html', c,
        context_instance=RequestContext(request))
