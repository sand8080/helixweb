from django.template import Library, Node, resolve_variable, TemplateSyntaxError,\
    VariableDoesNotExist

register = Library()


class UrlNode(Node):
    def __init__(self, url, nodelist):
        self.url = url.strip('"\'')
        self.nodelist = nodelist

    def _get_service_type(self):
        chunks = self.url.split('/')
        srv_types = filter(lambda x: len(x), chunks)
        return srv_types[0]

    def _get_service_rights(self, rights, srv_type):
        r = filter(lambda x: x.get('service_type', '') == srv_type, rights)
        if len(r):
            return r[0]
        else:
            return None

    def _get_action_name(self):
        chunks = self.url.split('/')
        srv_types = filter(lambda x: len(x), chunks)
        return srv_types[-1]

    def _is_url_allowed(self, rights):
        srv_type = self._get_service_type()
        action = self._get_action_name()
        r = self._get_service_rights(rights, srv_type)
        if r:
            return action in r.get('properties', [])
        else:
            return False

    def render(self, context):
        rended = self.nodelist.render(context).strip()
        try:
            rights = resolve_variable('rights', context)
            cur_lang = resolve_variable('cur_lang', context)
            if self._is_url_allowed(rights):
                return '<a href="/%(cur_lang)s/%(url)s">%(descr)s</a>' % \
                    {'cur_lang': cur_lang, 'url': self.url, 'descr': rended}
            else:
                return '<b style="color:red;">not allowed %s</b>' % rended
        except VariableDoesNotExist:
            return ''


@register.tag
def allowedurl(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError('%s tag requires exactly one argument'
            % bits[0])
    nodelist = parser.parse(('endallowedurl',))
    parser.delete_first_token()
    return UrlNode(bits[1], nodelist)