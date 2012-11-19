from django.conf import settings


BILLING_SERVICE_URL = getattr(settings, 'BILLING_SERVICE_URL',
    'http://localhost:10998')
