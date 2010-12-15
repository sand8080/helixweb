from helixweb.core.client import Client
from helixweb.auth import settings


def get_rights(session_id):
    c = Client(settings.AUTH_SERVICE_URL)
    resp = c.request({'action': 'get_user_rights',
        'session_id': session_id})
    if resp['status'] == 'ok':
        return resp['rights']
    else:
        return []

