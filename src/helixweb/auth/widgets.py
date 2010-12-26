from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import CheckboxInput, Widget
from django.utils.safestring import mark_safe


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
        output.append(u'<table class="services_properties bordered wide center">')
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
            cb = CheckboxInput(attrs)
            alignment = '&nbsp; &nbsp; &nbsp; &nbsp;'
            rendered_cb = cb.render(id_all, id_all in self.sel_props)
            output.append(u'<tr><td style="text-align:right;" colspan="%s">%s %s %s%s</td></tr>' %
                (self.COLUMNS * 2, _('select all'), rendered_cb, alignment, js_cb_all))

            props = srv['properties']
            props_idx = self._props_indexes(len(props), self.COLUMNS)
            rows = len(props_idx) / self.COLUMNS
            for r_idx in range(rows):
                output.append(u'<tr>')
                for c_idx in range(self.COLUMNS):
                    p_idx = props_idx[r_idx + c_idx * rows]
                    if p_idx != None:
                        p = props[p_idx]
                        id = '%s_%s' % (srv['id'], p)
                        attrs = {'id': id}
                        label_for = u' for="%s"' % id
                        cb = CheckboxInput(attrs)
                        rendered_cb = cb.render(id, id in self.sel_props)
                        output.append(u'<td><label%s>%s</label></td><td>%s %s</td>' %
                            (label_for, p, rendered_cb, alignment))
                    else:
                        output.append(u'<td colspan="2"></td>')
                output.append(u'</tr>')
        output.append(u'</table><br>')
        return mark_safe(u'\n'.join(output))

    def _elems_in_cols(self, total, col_num):
        result = [total / col_num] * col_num
        for i in range(total % col_num):
            result[i] += 1
        return result

    def _props_indexes(self, total, col_num):
        el_in_cols = self._elems_in_cols(total, col_num)
        rows = max(el_in_cols)
        result = [None] * (rows * col_num)
        prop_idx = 0
        for col_num, el_num in enumerate(el_in_cols):
            for i in range(el_num):
                result[col_num * rows + i] = prop_idx
                prop_idx += 1
        return result
