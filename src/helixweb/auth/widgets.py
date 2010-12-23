from itertools import chain

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import SelectMultiple, CheckboxInput
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


class ServicesWidget(forms.MultiWidget):
    def __init__(self, services, attrs=None):
        widgets = ([forms.TextInput(attrs=attrs) for _ in services])
        super(ServicesWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        print '#### decompress value: ', value
        if value:
            return value
        res = [None for _ in self.widgets]
        return res


class ServicesSelectMultiple(SelectMultiple):
    def __init__(self, services, *args, **kwargs):
        self.services = services
        super(ServicesSelectMultiple, self).__init__(*args, **kwargs)

    def render(self, name, value, services=None, attrs=None):
        print '### name, value, attrs', name, value, attrs
        value = [] if value is None else value
        final_attrs = self.build_attrs(attrs, name=name)
        output = []
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for srv in self.services:
            output.append(u'<table class="service_properties bordered wide"  style="text-align:right;">')
            output.append(u'<tr><th colspan="2">%s %s</th></tr>' % (_('service'), srv.get('name')))

            cb_all = u'''<script type="text/javascript">
                $("#%(name)s_all").click(function() {
                    var checked_status = this.checked;
                    $("input[name=%(name)s]").each(function() {
                        this.checked = checked_status;
                    });
                });
                </script>''' % ({'name': srv['name']})
            output.append(u'<tr><td colspan="2">%s <input type="checkbox" id="%s_all">%s</td></tr>' %
                (_('select all'), srv['name'], cb_all))

            for p in srv['properties']:
                id = attrs.get('id', '')
                final_attrs = dict(final_attrs, id='%s%s_%s' % (id, srv['id'], p))
                label_for = u' for="%s"' % final_attrs['id']

                cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
                rendered_cb = cb.render(srv.get('name'), '')
                output.append(u'<tr><td><label%s>%s</label></td><td>%s</td></tr>' %
                    (label_for, p, rendered_cb))

            output.append(u'<tr><td colspan="2"><br></td></tr>')
            output.append(u'</table>')
        return mark_safe(u'\n'.join(output))

#    def render(self, name, value, attrs=None, choices=()):
#        if value is None: value = []
#        has_id = attrs and 'id' in attrs
#        final_attrs = self.build_attrs(attrs, name=name)
#        output = [u'<ul>']
#        # Normalize to strings
#        str_values = set([force_unicode(v) for v in value])
#        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
#            # If an ID attribute was given, add a numeric index as a suffix,
#            # so that the checkboxes don't all have the same ID attribute.
#            if has_id:
#                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
#                label_for = u' for="%s"' % final_attrs['id']
#            else:
#                label_for = ''
#
#            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
#            option_value = force_unicode(option_value)
#            rendered_cb = cb.render(name, option_value)
#            option_label = conditional_escape(force_unicode(option_label))
#            output.append(u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label))
#        output.append(u'</ul>')
#        return mark_safe(u'\n'.join(output))


    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_
    id_for_label = classmethod(id_for_label)
