from django import template
from django.utils.translation import ugettext_lazy as _

from helixweb.settings import SUPPORTED_LANGS
from helixweb.core.localization import cur_lang as c_l

register = template.Library()


@register.inclusion_tag('lang_switcher.html', takes_context=True)
def lang_switcher(context):
    request = context['request']
    path = request.path
    d = c_l(request)
    cur_lang = _(d.get('cur_lang'))
    return {'langs': SUPPORTED_LANGS, 'path': path,
        'cur_lang': cur_lang}
