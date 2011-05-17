from django.template import (Library, Node, resolve_variable, TemplateSyntaxError,
    VariableDoesNotExist)

register = Library()


class UrlAccessChecker(object):
    def _get_service_rights(self, rights, srv_type):
        r = filter(lambda x: x.get('service_type', '') == srv_type, rights)
        if len(r):
            return r[0]
        else:
            return None

    def _get_action_name(self, url):
        chunks = url.split('/')
        srv_types = filter(lambda x: len(x), chunks)
        try:
            return srv_types[1]
        except IndexError:
            return ''

    def _get_service_type(self, url):
        chunks = url.split('/')
        srv_types = filter(lambda x: len(x), chunks)
        return srv_types[0]

    def is_url_allowed(self, url, rights):
        srv_type = self._get_service_type(url)
        action = self._get_action_name(url)
        r = self._get_service_rights(rights, srv_type)
        if r:
            return action in r.get('properties', [])
        else:
            return False


class UrlNode(Node):
    def __init__(self, nodelist, always_show_text=None):
        self.nodelist = nodelist
        self.always_show_text = always_show_text == 'True'

    def _get_url_params(self, rended):
        l = rended.split(None, 1)
        try:
            return l[0], l[1]
        except IndexError:
            raise TemplateSyntaxError('allowedurl tag value should contain ' +
                'space separated url and url description')

    def render(self, context):
        rended = self.nodelist.render(context).strip()
        url, descr = self._get_url_params(rended)

        try:
            rights = resolve_variable('rights', context)
            checker = UrlAccessChecker()
            if checker.is_url_allowed(url, rights):
                request = resolve_variable('request', context)
                cur_lang = resolve_variable('cur_lang', context)
                lang_url = '/%s%s' % (cur_lang, url)
                if lang_url == request.path:
                    return '<span class="current_item">%s</span>' % descr
                else:
                    return '<a href="%(lang_url)s">%(descr)s</a>' % \
                        {'lang_url': lang_url, 'descr': descr}
            elif self.always_show_text:
                return '%s' % descr
            else:
                return ''
        except VariableDoesNotExist:
            return ''


@register.tag
def allowedurl(parser, token):
    '''
    Usage:
    {% allowedurl show_text_param %}
        url_to_check showing_text
    {% endallowedurl %}
    show_text_param - default value False. To show text in case access
        denied to url set value to True.
    url_to_check - check access to url
    '''
    bits = token.split_contents()
    if len(bits) > 2:
        raise TemplateSyntaxError('%s tag requires one or no arguments'
            % bits[0])
    nodelist = parser.parse(('endallowedurl',))
    parser.delete_first_token()
    try:
        always_show_text = bits[1]
    except IndexError:
        always_show_text = None
    return UrlNode(nodelist, always_show_text)


@register.filter
def is_any_of_urls_allowed(urls, rights):
    '''
    Usage:
    urls|is_any_of_urls_allowed
    urls - comma separated urls
    Returns True or False
    '''
    checker = UrlAccessChecker()
    us = filter(lambda x: len(x) > 0, map(unicode.strip, urls.split(',')))
    for u in us:
        res = checker.is_url_allowed(u, rights)
        if res is True:
            return res
    return False


@register.filter
def is_url_allowed(url, rights):
    '''
    Usage:
    urls|is_url_allowed
    Returns True or False
    '''
    checker = UrlAccessChecker()
    return checker.is_url_allowed(url, rights)


@register.filter
def gen_urls_list(base_url, values):
    return ', '.join(['<a href="%s%s/">%s</a>' % (base_url, v, v) for v in values])
gen_urls_list.is_safe = True