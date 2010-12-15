from django.template import Library, Node, resolve_variable, TemplateSyntaxError,\
    VariableDoesNotExist

register = Library()


class UrlNode(Node):
    def __init__(self, nodelist, url, always_show_text=None):
        self.url = url.strip('"\'')
        self.nodelist = nodelist
        self.always_show_text = always_show_text == 'True'

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
            if self._is_url_allowed(rights):
                request = resolve_variable('request', context)
                cur_lang = resolve_variable('cur_lang', context)
                lang_url = '/%s%s' % (cur_lang, self.url)
                if lang_url == request.path:
                    return '<span class="current_item">%s</span>' % rended
                else:
                    return '<a href="/%(lang_url)s">%(descr)s</a>' % \
                        {'lang_url': lang_url, 'descr': rended}
            elif self.always_show_text:
                return '%s' % rended
            else:
                return ''
        except VariableDoesNotExist:
            return ''


@register.tag
def allowedurl(parser, token):
    bits = token.split_contents()
    if len(bits) not in (2, 3):
        raise TemplateSyntaxError('%s tag requires exactly one or two arguments'
            % bits[0])
    nodelist = parser.parse(('endallowedurl',))
    parser.delete_first_token()
    always_show_text = bits[2] if len(bits) > 2 else None
    return UrlNode(nodelist, bits[1], always_show_text)