from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import CheckboxInput, Widget
from django.forms import TextInput
from django.utils.safestring import mark_safe
from helixweb.core.views import elems_as_table


class ServicesSelectMultiple(Widget):
    COLUMNS = 3

    def __init__(self, *args, **kwargs):
        self.services = kwargs.pop('services', [])
        vars = args[0] if len(args) else {}
        self.sel_props = self._sel_props(vars, self.services)
        super(ServicesSelectMultiple, self).__init__(*args, **kwargs)

    def as_helix_request(self):
        result = []
        for s in self.services:
            s_id = u'%s_' % s.get('id')
            s_props = filter(lambda x: x.startswith(s_id), self.sel_props)
            skip = len(s_id)
            props = [p[skip:] for p in s_props]
            props = [p for p in s['properties'] if p in props]
            result.append({'service_id': s.get('id'), 'properties': props})
        return result

    def _sel_props(self, vars, services):
        sel_props = []
        for s in services:
            s_id = u'%s' % s['id']
            sel_props += filter(lambda x: x.startswith(s_id), vars.keys())
        return sel_props

    def render(self, name, value, attrs=None):
        value = [] if value is None else value
        output = []
        output.append(u'<table class="services_properties wide center">')
        for srv in self.services:
            output.append(u'<tr><th colspan="%s">%s</th></tr>' %
                (self.COLUMNS * 2, srv.get('name')))

            js_cb_all = u'''<script type="text/javascript">
                $("#%(id)s_all").click(function() {
                    var checked_status = this.checked;
                    $("input[name^=%(id)s]").each(function() {
                        this.checked = checked_status;
                    });
                });
                </script>''' % ({'id': srv['id']})

            id_all = '%s_all' % srv['id']
            attrs = {'id': id_all}
            label_for = u' for="%s"' % id_all
            cb = CheckboxInput(attrs)
            rendered_cb = cb.render(id_all, id_all in self.sel_props)
            output.append(u'<tr><td colspan="%s">%s <label%s>%s</label> %s</td></tr>' %
                (self.COLUMNS * 2, rendered_cb, label_for, _('select all'), js_cb_all))

            props = srv['properties']
            rended_props = []
            for p in props:
                id = '%s_%s' % (srv['id'], p)
                attrs = {'id': id}
                label_for = u' for="%s"' % id
                cb = CheckboxInput(attrs)
                rendered_cb = cb.render(id, id in self.sel_props)
                rended_props.append((rendered_cb, u'<label%s>%s</label>' % (label_for, p)))
            output.append(elems_as_table(rended_props, self.COLUMNS))
        output.append(u'</table><br>')
        return mark_safe(u'\n'.join(output))


class ConstInput(TextInput):
    def __init__(self, *args, **kwargs):
        super(ConstInput, self).__init__(*args, **kwargs)

    def render(self, *args, **kwargs):
        name = args[0]
        value = args[1]
        s_input = u'<input type="hidden" name="%s" value="%s">' % (name, value)
        return mark_safe(u'%s%s' % (s_input, value))