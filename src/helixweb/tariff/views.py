from django.shortcuts import render_to_response
from django.template import RequestContext

from helixweb.core.views import (login_redirector)
#from helixcore.server.client import Client

from helixweb.tariff import settings #@UnresolvedImport

#helix_cli = Client(settings.BILLING_SERVICE_URL)


@login_redirector
def description(request):
    return render_to_response('tariff_descr.html', {},
        context_instance=RequestContext(request))
