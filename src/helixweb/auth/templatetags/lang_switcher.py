from django import template

register = template.Library()

from helixweb.settings import SUPPORTED_LANGS

@register.inclusion_tag('lang_switcher.html')
def lang_switcher(lang):
    if lang in SUPPORTED_LANGS:
        cur_l = lang
    else:
        cur_l = SUPPORTED_LANGS[0] if len(SUPPORTED_LANGS) > 0 else 'ru'

    return {'current_lang': cur_l, 'langs': SUPPORTED_LANGS}

