from helixcore.server.client import Client

from helixweb.auth import settings


def get_rights(session_id, django_req):
    c = Client(settings.AUTH_SERVICE_URL)
    resp = c.request({'action': 'get_user_rights',
        'session_id': session_id}, django_req)
    if resp['status'] == 'ok':
        return resp['rights']
    else:
        return []

