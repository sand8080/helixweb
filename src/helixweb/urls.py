from django.conf.urls.defaults import * #@UnusedWildImport


urlpatterns = patterns('',
    (r'^auth/', include('helixweb.auth.urls')),
    (r'^billing/', include('helixweb.billing.urls')),
    (r'^tariff/', include('helixweb.tariff.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'static'}),
)
