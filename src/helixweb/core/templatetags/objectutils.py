from django.template import Library

register = Library()


@register.filter
def get(h, key):
    return h.get(key)