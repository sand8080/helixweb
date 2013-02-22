from django.conf import settings


AUTH_SERVICE_URL = getattr(settings, 'AUTH_SERVICE_URL',
    'http://localhost:10999')


LANGS = [(t[0], t[1].lower()) for t in getattr(settings, 'SUPPORTED_LANGS', [])]
DEFAULT_LANG = getattr(settings, 'DEFAULT_LANGUAGE_CODE', '').lower()
