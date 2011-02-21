from django import template
from helixweb.settings import SUPPORTED_SERVICES

register = template.Library()


@register.inclusion_tag('service_switcher.html', takes_context=True)
def service_switcher(context):
    return {'services': SUPPORTED_SERVICES,
        'cur_service': context['cur_service']}
