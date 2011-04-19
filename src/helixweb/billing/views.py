from functools import partial

from django.shortcuts import render_to_response
from django.template import RequestContext

from helixcore.server.client import Client

from helixweb.core.views import (login_redirector, _prepare_context)

from helixweb.billing import settings #@UnresolvedImport
from helixweb.billing.forms import CurrenciesForm


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
#    form = CurrenciesForm(request=request)

    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        print '### resp', resp
        form.handle_errors(resp)
    else:
        print '### form is invalid'
#    c['currencies_form'] = form
    return render_to_response('currency/list.html', c,
        context_instance=RequestContext(request))

