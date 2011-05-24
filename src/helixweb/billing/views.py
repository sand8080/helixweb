from functools import partial

from django.shortcuts import render_to_response
from django.template import RequestContext

from helixcore.server.client import Client

from helixweb.core.views import (login_redirector, _prepare_context,
    process_helix_response, _action_logs)

from helixweb.billing import settings #@UnresolvedImport
from helixweb.billing.forms import (CurrenciesForm, UsedCurrenciesForm,
    ModifyUsedCurrenciesForm, AddBalanceForm, BillingForm, ModifyBalanceForm)
from django.http import HttpResponseRedirect
from helixweb.billing.forms_filters import (FilterAllActionLogsForm,
    FilterSelfActionLogsForm, FilterBalanceForm)


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


def _prepare_action_logs_context(c):
    params = {'checking_url': '/billing/get_balances/',
        'user_info_url': '/billing/user_info/'}
    c.update(params)


@login_redirector
def action_logs(request):
    c = prepare_context(request)
    _prepare_action_logs_context(c)
    _action_logs(c, request, FilterAllActionLogsForm, helix_cli)
    return render_to_response('action_logs/billing_list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def action_logs_self(request):
    c = prepare_context(request)
    _prepare_action_logs_context(c)
    _action_logs(c, request, FilterSelfActionLogsForm, helix_cli)
    return render_to_response('action_logs/billing_list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def balances(request):
    c = prepare_context(request)
    resp = helix_cli.request(FilterBalanceForm.get_used_currencies_req(request))
    c.update(process_helix_response(resp, 'currencies', 'currencies_error'))
    currencies = resp.get('currencies', [])
    if len(request.GET) == 0 or (len(request.GET) == 1 and 'pager_offset' in request.GET):
        # setting default is_active value to True
        form = FilterBalanceForm({'is_active': 'all'}, currencies=currencies, request=request)
    else:
        form = FilterBalanceForm(request.GET, currencies=currencies, request=request)

    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        form.update_total(resp)
        c.update(process_helix_response(resp, 'balances', 'balances_error'))
        c['pager'] = form.pager
    c['form'] = form
    return render_to_response('balance/list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def user_balances(request, user_id):
    c = prepare_context(request)
    resp = helix_cli.request(BillingForm.get_user_balances_req(request, user_id))
    c.update(process_helix_response(resp, 'balances', 'balances_error'))
    c['user_id'] = user_id
    return render_to_response('balance/balances_self.html', c,
        context_instance=RequestContext(request))


def _add_balance(request, template, redirect_url, user_id=None):
    c = prepare_context(request)
    c['user_id'] = user_id
    c['action'] = AddBalanceForm.action
    resp = helix_cli.request(AddBalanceForm.get_used_currencies_req(request))
    c.update(process_helix_response(resp, 'currencies', 'currencies_error'))
    currencies = resp.get('currencies', [])
    if request.method == 'POST':
        form = AddBalanceForm(request.POST, currencies=currencies, request=request,
            user_id=user_id)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect(redirect_url)
    else:
        form = AddBalanceForm(currencies=currencies, request=request, user_id=user_id)
    c['form'] = form
    return render_to_response(template, c,
        context_instance=RequestContext(request))


@login_redirector
def add_balance(request):
    return _add_balance(request, 'balance/add.html',
        '/billing/get_balances/')


@login_redirector
def user_add_balance(request, user_id):
    return _add_balance(request, 'user/add_balance.html',
        '/billing/user_info/%s/' % user_id, user_id=user_id)


@login_redirector
def modify_balance(request, balance_id):
    c = prepare_context(request)
    c['action'] = ModifyBalanceForm.action
    if request.method == 'POST':
        form = ModifyBalanceForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect('/billing/get_balances/')
    else:
        resp = helix_cli.request(ModifyBalanceForm.get_balance_req(balance_id, request))
        c.update(process_helix_response(resp, 'balances', 'balances_error'))
        balance_info = {}
        if resp['status'] == 'ok' and len(resp['balances']) > 0:
            balance_info = resp['balances'][0]
        form = ModifyBalanceForm.from_balance_info(balance_info, request)
    c['form'] = form
    return render_to_response('balance/modify.html', c,
        context_instance=RequestContext(request))


@login_redirector
def balances_self(request):
    c = prepare_context(request)
    resp = helix_cli.request(BillingForm.get_balances_self_req(request))
    c.update(process_helix_response(resp, 'balances', 'balances_error'))
    return render_to_response('balance/balances_self.html', c,
        context_instance=RequestContext(request))


@login_redirector
def user_info(request, id):
    id = int(id)
    c = prepare_context(request)
    c['user_id'] = id
#    resp = helix_cli.request(HelixwebRequestForm.get_users_req(request, [id]))
#    c.update(process_helix_response(resp, 'users', 'users_error'))
#    c['user'] = _extract_user(resp)
    return render_to_response('user/billing_user_info.html', c,
        context_instance=RequestContext(request))
