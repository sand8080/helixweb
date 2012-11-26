from django.conf.urls.defaults import include, patterns #@UnusedWildImport
from django.views.generic.simple import redirect_to


urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': '/auth/'}),

    (r'^auth/', include('helixweb.auth.urls')),
    (r'^billing/', include('helixweb.billing.urls')),
    (r'^tariff/', include('helixweb.tariff.urls')),
)
