from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from helixweb.core.views import (login_redirector, process_helix_response)
from helixcore.server.client import Client

from helixweb.tariff import settings #@UnresolvedImport
from helixweb.tariff.forms import AddTarifficationObjectForm,\
    ModifyTarifficationObjectForm
from helixweb.tariff.forms_filters import FilterTarifficationObjectsForm

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
                    return HttpResponseRedirect('/tariff/get_tariffication_objects/')
    else:
        form = AddTarifficationObjectForm(request=request)
    c['form'] = form
    return render_to_response('tariffication_object/add.html', c,
        context_instance=RequestContext(request))


@login_redirector
def get_tariffication_objects(request):
    c = {}
    form = FilterTarifficationObjectsForm(request.GET, request=request)

    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        form.update_total(resp)
        c.update(process_helix_response(resp, 'tariffication_objects',
            'tariffication_objects_error'))
        c['pager'] = form.pager
    c['form'] = form
    return render_to_response('tariffication_object/list.html', c,
        context_instance=RequestContext(request))


@login_redirector
def modify_tariffication_object(request, to_id):
    c = {}
    if request.method == 'POST':
        form = ModifyTarifficationObjectForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect('/tariff/get_tariffication_objects/')
    else:
        resp = helix_cli.request(ModifyTarifficationObjectForm.get_tariffication_object_req(request, to_id))
        form = ModifyTarifficationObjectForm.from_get_helix_resp(resp, request)
        if form.is_valid():
            form.handle_errors(resp)
    c['form'] = form

    return render_to_response('tariffication_object/modify.html', c,
        context_instance=RequestContext(request))
