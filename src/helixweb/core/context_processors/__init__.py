from django.core.context_processors import csrf

from helixweb.core.localization import cur_lang
from helixweb.settings import SUPPORTED_SERVICES


def _get_session_id(request):
    return request.COOKIES.get('session_id', '')


def _get_user_id(request):
    return request.COOKIES.get('user_id')


def _get_current_service(request):
    path_info = request.path_info
    chunks = path_info.split('/')
    for chunk in chunks:
        if chunk in SUPPORTED_SERVICES:
            return chunk
    return None


def access_info(request):
    c = {}
    c['cur_service'] = _get_current_service(request)
    c.update(cur_lang(request))
    c.update(csrf(request))
    return c