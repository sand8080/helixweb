from django import template
from django.template.base import resolve_variable

from helixweb.settings import SUPPORTED_SERVICES

register = template.Library()


@register.inclusion_tag('service_switcher.html', takes_context=True)
def service_switcher(context):
    rights = resolve_variable('rights', context)
    # filtering services with permissions
    rights = filter(lambda x: len(x.get('properties', []))>0, rights)
    srvs = [x.get('service_type') for x in rights]
    # filtering supported services
    sup_srvs = filter(lambda x: x in srvs, SUPPORTED_SERVICES)
    return {'services': sup_srvs, 'cur_service': context['cur_service'],
        'cur_lang': context['cur_lang']}
