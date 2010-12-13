from django.template import Library, Node, resolve_variable

register = Library()


class NextPageNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        next_page_offset = self.nodelist.render(context).strip()
        req = resolve_variable('request', context)
        params = req.GET.copy()
        params['pager_offset'] = next_page_offset
        return '%s?%s' % (req.path, params.urlencode())


@register.tag
def nextpageurl(parser, token):
    nodelist = parser.parse(('endnextpageurl',))
    parser.delete_first_token()
    return NextPageNode(nodelist)