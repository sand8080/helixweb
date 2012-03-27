from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from helixweb.core.views import (login_redirector, process_helix_response)
from helixcore.server.client import Client

from helixweb.tariff import settings #@UnresolvedImport
from helixweb.tariff.forms import AddTarifficationObjectForm,\
    ModifyTarifficationObjectForm, DeleteTarifficationObjectForm, AddTariffForm
from helixweb.tariff.forms_filters import FilterTarifficationObjectsForm,\
    FilterTariffsForm

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


@login_redirector
def delete_tariffication_object(request, to_id):
    c = {}
    if request.method == 'POST':
        form = DeleteTarifficationObjectForm(request.POST, request=request)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                return HttpResponseRedirect('/tariff/get_tariffication_objects/')
    else:
        resp = helix_cli.request(DeleteTarifficationObjectForm.get_by_id_req(to_id, request))
        tos = resp.get('tariffication_objects', [{}])
        d_to = tos[0] if len(tos) else {}
        form = DeleteTarifficationObjectForm(d_to, request=request)
        if form.is_valid():
            form.handle_errors(resp)
    c['form'] = form
    return render_to_response('tariffication_object/delete.html', c,
        context_instance=RequestContext(request))


@login_redirector
def add_tariff(request):
    c = {}
    parent_tariffs = []
    if request.method == 'POST':
        form = AddTariffForm(request.POST, request=request,
            parent_tariffs=parent_tariffs)
        if form.is_valid():
            resp = helix_cli.request(form.as_helix_request())
            form.handle_errors(resp)
            if resp['status'] == 'ok':
                if request.POST.get('stay_here', '0') != '1':
                    return HttpResponseRedirect('/tariff/get_tariffs/')
    else:
        form = AddTariffForm(request=request)
    c['form'] = form
    return render_to_response('tariff/add.html', c,
        context_instance=RequestContext(request))



@login_redirector
def get_tariffs(request):
    c = {}
    form = FilterTariffsForm(request.GET, request=request)
    if form.is_valid():
        resp = helix_cli.request(form.as_helix_request())
        c.update(process_helix_response(resp, 'tariffs', 'tariffs_error'))
    c['form'] = form
    return render_to_response('tariff/list.html', c,
        context_instance=RequestContext(request))
