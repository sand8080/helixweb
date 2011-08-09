from helixweb.core.context_processors import _get_session_id, _get_user_id
from helixweb.core.security import get_rights


def _billing_rights(rights):
    for r in rights:
        if r.get('service_type') == 'billing':
            return r.get('properties', [])
    return []


def _access_to_billing_user_info(c):
    rights = c.get('rights', [])
    billing_rights = _billing_rights(rights)
    requires = ('add_balance', 'get_balances', 'get_action_logs')
    for req in requires:
        if req in billing_rights:
            c['access_to_billing_user_info'] = True
            return
    c['access_to_billing_user_info'] = False


def auth_access_info(request):
    c = {}
    if request.path_info.startswith('/auth/add_environment'):
        c['logged_in'] = False
        c['rights'] = {}
        c['logged_user_id'] = None
    else:
        c['logged_in'] = True
        c['logged_user_id'] = _get_user_id(request)
        c['rights'] = get_rights(_get_session_id(request))
    _access_to_billing_user_info(c)
    return c