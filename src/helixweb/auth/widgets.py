from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import SelectMultiple, CheckboxInput, Widget
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.util import flatatt


class ServicesSelectMultiple(Widget):
    def __init__(self, *args, **kwargs):
        self.services = kwargs.pop('services', [])
        vars = args[0] if len(args) else {}
        self.sel_props = self._sel_props(vars, self.services)
        print '### SEL PROPS ALL: ', self.sel_props
        super(ServicesSelectMultiple, self).__init__(*args, **kwargs)

    def _sel_props(self, vars, services):
        sel_props = []
        for s in services:
            s_id = u'%s' % s['id']
            sel_props += filter(lambda x: x.startswith(s_id), vars.keys())
        return sel_props

    def render(self, name, value, services=None, attrs=None):
        value = [] if value is None else value
        output = []
        # Normalize to strings
        for srv in self.services:
            output.append(u'<table class="service_properties bordered wide">')
            output.append(u'<tr><th colspan="2">%s</th></tr>' % srv.get('name'))

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
            cb = CheckboxInput(attrs)
            rendered_cb = cb.render(id_all, id_all in self.sel_props)
            output.append(u'<tr><td colspan="2" style="text-align:right;">%s %s %s</td></tr>' %
                (_('select all'), rendered_cb, js_cb_all))

            for p in srv['properties']:
                id = '%s_%s' % (srv['id'], p)
                attrs = {'id': id}
                label_for = u' for="%s"' % id
                cb = CheckboxInput(attrs)
                rendered_cb = cb.render(id, id in self.sel_props)
                output.append(u'<tr><td><label%s>%s</label></td><td style="text-align:right;">%s</td></tr>' %
                    (label_for, p, rendered_cb))

            output.append(u'<tr><td colspan="2"><br></td></tr>')
            output.append(u'</table>')
        return mark_safe(u'\n'.join(output))
