import base64

from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from helixweb.error import UnauthorizedActivity


def login_redirector(func):
    def decorated(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except UnauthorizedActivity:
            b_url = base64.encodestring(request.get_full_path())
            return HttpResponseRedirect('/auth/login/?backurl=%s' % b_url)
    return decorated


def process_helix_response(resp, f_name, f_err_name):
    if resp['status'] != 'ok':
        return {f_err_name: resp['code']}
    else:
        return {f_name: resp[f_name]}


def separate_elems_by_columns(total, col_num):
    result = [total / col_num] * col_num
    for i in range(total % col_num):
        result[i] += 1
    return result

def elems_indexes_by_columns(total, col_num):
    el_in_cols = separate_elems_by_columns(total, col_num)
    rows = max(el_in_cols)
    result = [None] * (rows * col_num)
    prop_idx = 0
    for col_num, el_num in enumerate(el_in_cols):
        for i in range(el_num):
            result[col_num * rows + i] = prop_idx
            prop_idx += 1
    return result


def _make_empty_elem(elems):
    result = u'<td colspan="%s"></td>'
    for el in elems:
        if el:
            if isinstance(el, (list, tuple)):
                return result % len(el)
            else:
                return result % 1


def elems_as_table(elems, col_num):
    output = []
    elems_idx = elems_indexes_by_columns(len(elems), col_num)
    rows = len(elems_idx) / col_num
    empty_elem = _make_empty_elem(elems)
    for r_idx in range(rows):
        output.append(u'<tr>')
        for c_idx in range(col_num):
            el_idx = elems_idx[r_idx + c_idx * rows]
            if el_idx != None:
                el = elems[el_idx]
                if isinstance(el, (list, tuple)):
                    for el_part in el:
                        output.append(u'<td>%s</td>' % el_part)
                else:
                    output.append(u'<td>%s</td>' % el)
            else:
                output.append(empty_elem)
        output.append(u'</tr>')
    return mark_safe(u'\n'.join(output))
