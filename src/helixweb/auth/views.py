from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf

from helixweb.auth.forms import LoginForm
from helixweb.core.localization import cur_lang
#from django.utils.translation import ugettext as _

def login(request):
    c = {}
    c.update(csrf(request))
    c.update(cur_lang(request))
    if request.method == 'POST':
        form = LoginForm(request.POST, prefix='login')
        if form.is_valid():
            form.request()
            print 'ok'
        else:
            print 'failure'
#            return HttpResponseRedirect('/auth/success/')
    else:
        form = LoginForm(prefix='login')
    c['login_form'] = form
    return render_to_response('login.html', c,
        context_instance=RequestContext(request))
