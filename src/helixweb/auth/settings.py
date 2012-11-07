from django.conf import settings


AUTH_SERVICE_URL = getattr(settings, 'AUTH_SERVICE_URL',
    'http://localhost:11999')
