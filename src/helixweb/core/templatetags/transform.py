from django.template import Library
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from helixweb.core.views import elems_as_table

register = Library()


@register.filter
def listtotable(values, col_num):
    values = map(force_unicode, values)
    values = [conditional_escape(v) for v in values]
    return mark_safe(elems_as_table(values, col_num))
listtotable.is_safe = True

