from django.conf import settings


TARIFF_SERVICE_URL = getattr(settings, 'TARIFF_SERVICE_URL',
    'http://localhost:10997')
