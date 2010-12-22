from django.conf.urls.defaults import patterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^login/', 'auth.views.login'),

#    (r'^users/(?P<user_id>\d+)/$', 'auth.views.user'),
    (r'^modify_environment/$', 'auth.views.modify_environment'),

    (r'^get_services/$', 'auth.views.services'),
    (r'^add_service/$', 'auth.views.add_service'),
    (r'^modify_service/(?P<srv_id>\d+)/$', 'auth.views.modify_service'),

    (r'^get_groups/$', 'auth.views.groups'),
    (r'^add_group/$', 'auth.views.add_group'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
