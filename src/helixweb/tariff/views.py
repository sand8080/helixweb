from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from helixweb.core.views import (login_redirector)
from helixcore.server.client import Client

from helixweb.tariff import settings #@UnresolvedImport
from helixweb.tariff.forms import AddTarifficationObjectForm

helix_cli = Client(settings.TARIFF_SERVICE_URL)


@login_redirector
def description(request):
    return render_to_response('tariff_descr.html', {},
        context_instance=RequestContext(request))


@login_redirector
def add_tariffication_object(request):
    c = {}
    if request.method == 'POST':
        form = AddTarifficationObjectForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect('/tariff/')
    else:
        form = AddTarifficationObjectForm(request=request)
    c['form'] = form
    return render_to_response('tariffication_object/add.html', c,
        context_instance=RequestContext(request))
