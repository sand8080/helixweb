import base64
import json
import iso8601

from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from helixweb.core.localization import cur_lang_value
from helixcore.error import UnauthorizedActivity


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


def _action_logs(context, request, form_cls, helix_client):
    if request.method == 'GET':
        form = form_cls(request.GET, request=request)
    else:
        form = form_cls({}, request=request)
    if form.is_valid():
        resp = helix_client.request(form.as_helix_request(), request)
        form.update_total(resp)
        if 'action_logs' in resp:
            resp['action_logs'] = map(_prepare_action_log, resp['action_logs'])
        context.update(process_helix_response(resp, 'action_logs', 'action_logs_error'))
        context['pager'] = form.pager
    context['form'] = form


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


#def _prepare_context(request, cur_service=None):
#    c = {}
#    c['rights'] = get_rights(_get_session_id(request), request)
#    c['logged_in'] = True
#    c['cur_service'] = cur_service
#    c['logged_user_id'] = _get_user_id(request)
#    c.update(cur_lang(request))
#    c.update(csrf(request))
#    return c


def get_backurl(request):
    default_url = '/%s/auth/' % cur_lang_value(request)
    if 'backurl' in request.GET:
        try:
            return base64.decodestring(request.GET['backurl'])
        except Exception:
            return default_url
    else:
        return default_url


def build_index(helix_resp, field):
    ds = helix_resp.get(field, [])
    ds_idx = {}
    for d in ds:
        ds_idx[d['id']] = d
    return ds_idx


def _prepare_date(d, field_name):
    if field_name in d:
        d[field_name] = iso8601.parse_date(d[field_name])


def _prepare_action_log(a_log):
    _prepare_date(a_log, 'request_date')
    a_log['request'] = json.loads(a_log['request'])
    a_log['response'] = json.loads(a_log['response'])
    return a_log
