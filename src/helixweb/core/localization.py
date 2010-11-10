from helixweb.settings import SUPPORTED_LANGS, DEFAULT_LANGUAGE_CODE


def cur_lang(request):
    path = request.path
    sep = '/'
    tokens = path.strip(sep).split(sep)
    c_lang = tokens[0]
    langs = [l[0] for l in SUPPORTED_LANGS]
    c_lang = c_lang if c_lang in langs else DEFAULT_LANGUAGE_CODE
    return {'cur_lang': c_lang}