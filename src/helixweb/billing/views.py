from django.shortcuts import render_to_response
from django.template import RequestContext

from helixweb.core.views import (login_redirector, process_helix_response,
    _action_logs, _prepare_action_log, _prepare_date)
from helixcore.server.client import Client

from helixweb.billing import settings #@UnresolvedImport
from helixweb.billing.forms import (CurrenciesForm, UsedCurrenciesForm,
    ModifyUsedCurrenciesForm, AddBalanceForm, ModifyBalanceForm,
    BalanceForm, AddReceiptForm, AddBonusForm, LockForm)
from django.http import HttpResponseRedirect
from helixweb.billing.forms_filters import (FilterAllActionLogsForm,
    FilterSelfActionLogsForm, FilterBalanceForm, FilterUserActionLogsForm,
    FilterUserLocksForm, FilterLocksForm, FilterSelfLocksForm,
    FilterUserBalanceLocksForm)


helix_cli = Client(settings.BILLING_SERVICE_URL)


@login_redirector
def description(request):
    return render_to_response('billing_descr.html', {},
        context_instance=RequestContext(request))


@login_redirector
def currencies(request):
    c = {}
    form = CurrenciesForm({'ordering_params': ['-code']}, request=request)
    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        c.update(process_helix_response(resp, 'currencies', 'currencies_error'))
    return render_to_response('currency/list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def used_currencies(request):
    c = {}
    form = UsedCurrenciesForm({'ordering_params': ['-code']}, request=request)
    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        c.update(process_helix_response(resp, 'currencies', 'currencies_error'))
    return render_to_response('currency/used_list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def modify_used_currencies(request):
    c = {}
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
    c = {}
    _prepare_action_logs_context(c)
    _action_logs(c, request, FilterAllActionLogsForm, helix_cli)
    return render_to_response('action_logs/billing_list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def action_logs_self(request):
    c = {}
    _prepare_action_logs_context(c)
    _action_logs(c, request, FilterSelfActionLogsForm, helix_cli)
    return render_to_response('action_logs/billing_list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def user_action_logs(request, user_id):
    c = {}
    c['action'] = FilterUserActionLogsForm.action
    c['user_id'] = user_id
    _prepare_action_logs_context(c)
    if request.method == 'GET':
        form = FilterUserActionLogsForm(request.GET, request=request, id=user_id)
    else:
        form = FilterUserActionLogsForm({}, request=request, id=user_id)
    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        form.update_total(resp)
        if 'action_logs' in resp:
            resp['action_logs'] = map(_prepare_action_log, resp['action_logs'])
        c.update(process_helix_response(resp, 'action_logs', 'action_logs_error'))
        c['pager'] = form.pager
    c['form'] = form
    return render_to_response('user/billing_user_action_logs.html', c,
        context_instance=RequestContext(request))


@login_redirector
def balances(request):
    c = {}
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
        balances = resp.get('balances', [])
        c['pager'] = form.pager
    c['form'] = form
    return render_to_response('balance/list.html', c,
        context_instance=RequestContext(request))


def _locking_order_as_text(locking_order):
    try:
        idx = LockForm.locking_choices_billing_values.index(locking_order)
        return LockForm.locking_choices_sel_names[idx]
    except ValueError:
        return None


@login_redirector
def user_balances(request, user_id):
    c = {}
    c['action'] = 'get_balances'
    c['user_id'] = user_id
    resp = helix_cli.request(BalanceForm.get_user_balances_req(request, user_id))
    c.update(process_helix_response(resp, 'balances', 'balances_error'))
    balances = resp.get('balances', [])
    return render_to_response('user/balances.html', c,
        context_instance=RequestContext(request))


@login_redirector
def balances_self(request):
    c = {}
    c['action'] = 'get_balances_self'
    resp = helix_cli.request(BalanceForm.get_balances_self_req(request))
    c.update(process_helix_response(resp, 'balances', 'balances_error'))
    balances = resp.get('balances', [])
    return render_to_response('balance/balances_self.html', c,
        context_instance=RequestContext(request))


def _add_balance(request, template, redirect_url, user_id=None):
    c = {}
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


def _modify_balance(request, template, redirect_url, balance_id, user_id=None):
    c = {}
    c['action'] = ModifyBalanceForm.action
    c['user_id'] = user_id
    if request.method == 'POST':
        form = ModifyBalanceForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect(redirect_url)
    else:
        resp = helix_cli.request(ModifyBalanceForm.get_balance_req(request, balance_id))
        c.update(process_helix_response(resp, 'balances', 'balances_error'))
        balance_info = {}
        if resp['status'] == 'ok' and len(resp['balances']) > 0:
            balance_info = resp['balances'][0]
        form = ModifyBalanceForm.from_balance_info(balance_info, request)
    c['form'] = form
    return render_to_response(template, c,
        context_instance=RequestContext(request))


@login_redirector
def modify_balance(request, balance_id):
    return _modify_balance(request, 'balance/modify.html',
        '/billing/get_balances/', balance_id)


@login_redirector
def user_modify_balance(request, user_id, balance_id):
    return _modify_balance(request, 'user/modify_balance.html',
        '/billing/get_balances/%s/' % user_id, balance_id, user_id=user_id)


@login_redirector
def user_info(request, id):
    id = int(id)
    c = {}
    c['user_id'] = id
    return render_to_response('user/billing_user_info.html', c,
        context_instance=RequestContext(request))


def _add_money(request, form_cls, template, redirect_url, user_id, balance_id):
    c = {}
    c['action'] = form_cls.action
    c['user_id'] = user_id
    resp = helix_cli.request(form_cls.get_balance_req(request, balance_id))
    c.update(process_helix_response(resp, 'balances', 'balances_error'))
    if resp['total'] != 1:
        balance = {}
    else:
        balance = resp['balances'][0]
    c['balance'] = balance
    currency_code = balance.get('currency_code')
    if request.method == 'POST':
        form = form_cls(request.POST, request=request,
            balance_id=balance_id, currency_code=currency_code)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect(redirect_url)
    else:
        form = form_cls(balance_id=balance_id, currency_code=currency_code,
            request=request)
    c['form'] = form
    return render_to_response(template, c,
        context_instance=RequestContext(request))


@login_redirector
def user_add_receipt(request, user_id, balance_id):
    return _add_money(request, AddReceiptForm, 'user/add_receipt.html',
        '/billing/get_balances/%s/' % user_id, user_id, balance_id)


@login_redirector
def user_add_bonus(request, user_id, balance_id):
    return _add_money(request, AddBonusForm, 'user/add_bonus.html',
        '/billing/get_balances/%s/' % user_id, user_id, balance_id)


@login_redirector
def user_lock(request, user_id, balance_id):
    return _add_money(request, LockForm, 'user/lock.html',
        '/billing/get_balances/%s/' % user_id, user_id, balance_id)


def _locks(request, form_cls, template, user_id, balance_id):
    c = {}
    c['action'] = FilterUserLocksForm.action
    c['user_id'] = user_id
    c['balance_id'] = balance_id

    if len(request.GET) == 0 or (len(request.GET) == 1 and 'pager_offset' in request.GET):
        form = form_cls({'user_id': user_id, 'balance_id': balance_id},
            request=request)
    else:
        form = form_cls(request.GET, request=request)

    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        form.update_total(resp)
        c.update(process_helix_response(resp, 'locks', 'locks_error'))
        locks = resp.get('locks', [])
        for lock in locks:
            _prepare_date(lock, 'creation_date')
        c['locks'] = locks
        c['pager'] = form.pager
    c['form'] = form
    return render_to_response(template, c,
        context_instance=RequestContext(request))


@login_redirector
def locks(request):
    return _locks(request, FilterLocksForm, 'balance/locks.html',
        None, None)


@login_redirector
def user_balance_locks(request, user_id, balance_id):
    return _locks(request, FilterUserBalanceLocksForm, 'user/balance_locks.html',
        user_id, balance_id)


@login_redirector
def locks_self(request):
    return _locks(request, FilterSelfLocksForm, 'balance/locks_self.html',
        None, None)