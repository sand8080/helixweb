from helixweb.settings import SUPPORTED_LANGS, DEFAULT_LANGUAGE_CODE


def cur_lang_value(request):
    path = request.path
    sep = '/'
    tokens = path.strip(sep).split(sep)
    c_lang = tokens[0]
    langs = [l[0] for l in SUPPORTED_LANGS]
    c_lang = c_lang if c_lang in langs else DEFAULT_LANGUAGE_CODE
    return c_lang


def cur_lang(request):
    return {'cur_lang': cur_lang_value(request)}
