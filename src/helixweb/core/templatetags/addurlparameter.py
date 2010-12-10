#Example usage in html template:
#   <a href="{% addurlparameter sort 1 %}">Sort on field 1</a>
#   <a href="{% addurlparameter output pdf %}">Export as pdf</a>

from django.template import Library, Node, resolve_variable, TemplateSyntaxError

register = Library()


class AddParameter(Node):
    def __init__(self, varname, value):
        self.varname = varname
        self.value = value

    def render(self, context):
        req = resolve_variable('request', context)
        params = req.GET.copy()
        params[self.varname] = self.value
        return '%s?%s' % (req.path, params.urlencode())


@register.tag
def addurlparameter(parser, token):
    c = token.split_contents()
    if len(c) < 3:
        raise TemplateSyntaxError('addurlparameter tag requires two arguments')
    return AddParameter(c[1], c[2])
