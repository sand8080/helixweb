from helixweb.settings import SUPPORTED_LANGS, LANGUAGE_CODE


def cur_lang(request):
    path = request.path
    sep = '/'
    tokens = path.strip(sep).split(sep)
    c_lang = tokens[0]
    c_lang = c_lang if c_lang in SUPPORTED_LANGS else LANGUAGE_CODE
    return {'cur_lang': c_lang}