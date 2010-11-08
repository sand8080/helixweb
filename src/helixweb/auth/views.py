from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader, RequestContext
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
import cjson

from helixweb.auth import settings
from helixweb.auth.forms import LoginForm
from helixweb.core.client import Client
from helixweb.core.localization import cur_lang


def success(request):
    return render_to_response('success.html')


def failure(request):
    return render_to_response('failure.html')


def login(request):
    c = {}
    c.update(csrf(request))
    c.update(cur_lang(request))
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/auth/success/')
    else:
        form = LoginForm()
    c['form'] = form
    c['lang'] = request.COOKIES.get('lang')
    return render_to_response('login.html', c,
        context_instance=RequestContext(request))
