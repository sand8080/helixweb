from functools import partial
from datetime import datetime, timedelta

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf

from helixcore.server.client import Client

from helixweb.core.localization import cur_lang
from helixweb.core.views import (login_redirector, process_helix_response,
    build_index, get_backurl, _prepare_context, _prepare_action_log,
    _action_logs)
from helixweb.core.forms import HelixwebRequestForm

from helixweb.auth.forms import (LoginForm, AddServiceForm, ModifyServiceForm,
    ModifyEnvironmentForm, AddGroupForm, DeleteGroupForm, ModifyGroupForm,
    ModifyUserSelfForm, AddUserForm, LogoutForm, AddEnvironmentForm,
    ModifyUserForm)
from helixweb.auth.forms_filters import (FilterServiceForm, FilterGroupForm,
    FilterUserForm, FilterUserActionLogsForm, FilterAllActionLogsForm,
    FilterSelfActionLogsForm)
from helixweb.auth import settings


helix_cli = Client(settings.AUTH_SERVICE_URL)


prepare_context = partial(_prepare_context, cur_service='auth')


def _make_login(form, request):
    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request(), check_response=False)
        form.handle_errors(resp)
        status = resp.get('status')
        s_id = resp.get('session_id')
        if status == 'ok' and s_id is not None:
            # TODO: set secure cookie
            b_url = get_backurl(request)
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
    c = prepare_context(request)
    return render_to_response('auth_descr.html', c,
        context_instance=RequestContext(request))


@login_redirector
def add_service(request):
    c = prepare_context(request)
    if request.method == 'POST':
        form = AddServiceForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect('/auth/get_services/')
    else:
        form = AddServiceForm(request=request)
    c['form'] = form
    return render_to_response('service/add.html', c,
        context_instance=RequestContext(request))


@login_redirector
def modify_service(request, id):
    c = prepare_context(request)
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
    c = prepare_context(request)
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
    c = prepare_context(request)
    if request.method == 'POST':
        form = ModifyEnvironmentForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect('/auth/')
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
    c = prepare_context(request)
    resp = helix_cli.request(AddUserForm.get_active_groups_req(request))
    c.update(process_helix_response(resp, 'groups', 'groups_error'))
    groups = resp.get('groups', [])
    if request.method == 'POST':
        form = AddUserForm(request.POST, groups=groups, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
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
    c = prepare_context(request)
    resp = helix_cli.request(FilterUserForm.get_active_groups_req(request))
    c.update(process_helix_response(resp, 'groups', 'groups_error'))
    groups_idx = build_index(resp, 'groups')
    c['groups_idx'] = groups_idx

    resp = helix_cli.request(FilterUserForm.get_services_req(request))
    c.update(process_helix_response(resp, 'services', 'services_error'))
    c['services_idx'] = build_index(resp, 'services')

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


def _extract_user(helix_resp):
    users = helix_resp.get('users', [])
    if len(users) == 1:
        return dict(users[0])
    else:
        return {}


@login_redirector
def user_info(request, id):
    id = int(id)
    c = prepare_context(request)
    resp = helix_cli.request(HelixwebRequestForm.get_users_req(request, [id]))
    c.update(process_helix_response(resp, 'users', 'users_error'))
    c['user'] = _extract_user(resp)
    return render_to_response('user/user_info.html', c,
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
    c = prepare_context(request)
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


def _get_user_info(request, c, id):
    resp = helix_cli.request(ModifyUserForm.get_users_req(id, request))
    c.update(process_helix_response(resp, 'users', 'users_error'))
    user = {}
    if 'users' in resp:
        if len(resp['users']) != 1:
            c['users_error'] = 'HELIXAUTH_USER_ACCESS_DENIED'
        else:
            user = resp['users'][0]
    return user


@login_redirector
def modify_user(request, id):
    c = prepare_context(request)
    c['action'] = ModifyUserForm.action
    resp = helix_cli.request(ModifyUserForm.get_active_groups_req(request))
    c.update(process_helix_response(resp, 'groups', 'groups_error'))
    groups = resp.get('groups', [])
    user = _get_user_info(request, c, id)
    c['user'] = user
    if request.method == 'POST':
        form = ModifyUserForm(request.POST, groups=groups, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                new_login = request.POST.get('new_login')
                if new_login:
                    c['user']['login'] = new_login
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect('/auth/user_info/%s' % user['id'])
    else:
        form = ModifyUserForm.from_user_info(user, groups, request)
    c['form'] = form
    return render_to_response('user/modify_user.html', c,
        context_instance=RequestContext(request))


@login_redirector
def user_action_logs(request, id):
    c = prepare_context(request)
    c['action'] = FilterUserActionLogsForm.action
    _prepare_action_logs_context(c)
    user = _get_user_info(request, c, id)
    c['user'] = user
    if request.method == 'GET':
        form = FilterUserActionLogsForm(request.GET, request=request, id=id)
    else:
        form = FilterUserActionLogsForm({}, request=request, id=id)
    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        form.update_total(resp)
        if 'action_logs' in resp:
            resp['action_logs'] = map(_prepare_action_log, resp['action_logs'])
        c.update(process_helix_response(resp, 'action_logs', 'action_logs_error'))
        c['pager'] = form.pager
    c['form'] = form
    return render_to_response('user/user_action_logs.html', c,
        context_instance=RequestContext(request))


@login_redirector
def groups(request):
    c = prepare_context(request)
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
    c = prepare_context(request)
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
                    return HttpResponseRedirect('/auth/get_groups/')
    else:
        form = AddGroupForm(services=services, request=request)

    c['add_group_form'] = form
    return render_to_response('group/add.html', c,
        context_instance=RequestContext(request))


@login_redirector
def delete_group(request, id):
    c = prepare_context(request)
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
    c = prepare_context(request)
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


def _prepare_action_logs_context(c):
    params = {'checking_url': '/auth/get_users/',
        'user_info_url': '/auth/user_info/'}
    c.update(params)


@login_redirector
def action_logs(request):
    c = prepare_context(request)
    _prepare_action_logs_context(c)
    _action_logs(c, request, FilterAllActionLogsForm, helix_cli)
    return render_to_response('action_logs/auth_list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def action_logs_self(request):
    c = prepare_context(request)
    _prepare_action_logs_context(c)
    _action_logs(c, request, FilterSelfActionLogsForm, helix_cli)
    return render_to_response('action_logs/auth_list.html', c,
        context_instance=RequestContext(request))
