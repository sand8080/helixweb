from django.conf import settings


SENTRY_SERVICE_URL = getattr(settings, 'SENTRY_SERVICE_URL',
    'http://localhost:10997')
