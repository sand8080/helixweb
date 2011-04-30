from functools import partial

from django.shortcuts import render_to_response
from django.template import RequestContext

from helixcore.server.client import Client

from helixweb.core.views import (login_redirector, _prepare_context,
    process_helix_response, _action_logs)

from helixweb.billing import settings #@UnresolvedImport
from helixweb.billing.forms import (CurrenciesForm, UsedCurrenciesForm,
    ModifyUsedCurrenciesForm)
from django.http import HttpResponseRedirect
from helixweb.billing.forms_filters import (FilterAllActionLogsForm,
    FilterSelfActionLogsForm)


helix_cli = Client(settings.BILLING_SERVICE_URL)


prepare_context = partial(_prepare_context, cur_service='billing')


@login_redirector
def description(request):
    c = prepare_context(request)
    return render_to_response('billing_descr.html', c,
        context_instance=RequestContext(request))


@login_redirector
def currencies(request):
    c = prepare_context(request)
    form = CurrenciesForm({'ordering_params': ['-code']}, request=request)
    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        c.update(process_helix_response(resp, 'currencies', 'currencies_error'))
    return render_to_response('currency/list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def used_currencies(request):
    c = prepare_context(request)
    form = UsedCurrenciesForm({'ordering_params': ['-code']}, request=request)
    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        c.update(process_helix_response(resp, 'currencies', 'currencies_error'))
    return render_to_response('currency/used_list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def modify_used_currencies(request):
    c = prepare_context(request)

    resp = helix_cli.request(ModifyUsedCurrenciesForm.get_currencies_req(request))
    c.update(process_helix_response(resp, 'currencies', 'currencies_error'))
    currencies = resp.get('currencies', [])

    if request.method == 'POST':
        form = ModifyUsedCurrenciesForm(request.POST, currencies=currencies, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect('/billing/get_used_currencies/')
    else:
        resp = helix_cli.request(ModifyUsedCurrenciesForm.get_used_currencies_req(request))
        c.update(process_helix_response(resp, 'currencies', 'used_currencies_error'))
        used_currs = resp.get('currencies', [])
        used_currs_codes = [curr['code'] for curr in used_currs]
        d = {'new_currencies_codes': used_currs_codes}
        form = ModifyUsedCurrenciesForm(d, currencies=currencies, request=request)
        if form.is_valid():
            form.handle_errors(resp)
    c['form'] = form
    return render_to_response('currency/modify_used_currencies.html', c,
        context_instance=RequestContext(request))


@login_redirector
def action_logs(request):
    c = prepare_context(request)
    _action_logs(c, request, FilterAllActionLogsForm, helix_cli)
    return render_to_response('action_logs/billing_list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def action_logs_self(request):
    c = prepare_context(request)
    _action_logs(c, request, FilterSelfActionLogsForm, helix_cli)
    return render_to_response('action_logs/billing_list.html', c,
        context_instance=RequestContext(request))
