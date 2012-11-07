from helixweb.core.context_processors import _get_session_id, _get_user_id
from helixweb.core.security import get_rights


def _srv_rights(rights, srv_type):
    for r in rights:
        if r.get('service_type') == srv_type:
            return r.get('properties', [])
    return []


def _access_to_service_user_info(c, srv_type, req_rights, result_ctx_param_name):
    rights = c.get('rights', [])
    srv_rights = _srv_rights(rights, srv_type)
    for req in req_rights:
        if req in srv_rights:
            c[result_ctx_param_name] = True
            return
    c[result_ctx_param_name] = False


def _access_to_billing_user_info(c):
    srv_type = 'billing'
    req_rights = ('add_balance', 'get_balances', 'get_action_logs')
    result_ctx_param_name = 'access_to_billing_user_info'
    _access_to_service_user_info(c, srv_type, req_rights, result_ctx_param_name)


def auth_access_info(request):
    c = {}
    if request.path_info.startswith(('/auth/add_environment',
        '/auth/login')):
        c['logged_in'] = False
        c['rights'] = {}
        c['logged_user_id'] = None
    else:
        c['logged_in'] = True
        c['logged_user_id'] = _get_user_id(request)
        c['rights'] = get_rights(_get_session_id(request))
    _access_to_billing_user_info(c)
    return c