from django.conf.urls.defaults import patterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^login/', 'auth.views.login'),
#    (r'^users/(?P<user_id>\d+)/$', 'auth.views.user'),
    (r'^services/$', 'auth.views.services'),
    (r'^services/add/$', 'auth.views.add_service'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
