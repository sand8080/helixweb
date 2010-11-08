from django import template

from helixweb.settings import SUPPORTED_LANGS
from helixweb.core.localization import cur_lang

register = template.Library()


@register.inclusion_tag('lang_switcher.html', takes_context=True)
def lang_switcher(context):
    request = context['request']
    path = request.path
    d = cur_lang(request)
    c_lang = d.get('cur_lang')
    return {'langs': SUPPORTED_LANGS, 'path': path,
        'cur_lang': c_lang}
