from django.conf.urls.defaults import patterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'auth.views.description'),

    (r'^login/', 'auth.views.login'),
    (r'^logout/', 'auth.views.logout'),

    (r'^modify_environment/$', 'auth.views.modify_environment'),

    (r'^modify_user_self/$', 'auth.views.modify_user_self'),

    (r'^get_services/$', 'auth.views.services'),
    (r'^add_service/$', 'auth.views.add_service'),
    (r'^modify_service/(?P<id>\d+)/$', 'auth.views.modify_service'),

    (r'^get_groups/$', 'auth.views.groups'),
    (r'^add_group/$', 'auth.views.add_group'),
    (r'^delete_group/(?P<id>\d+)/$', 'auth.views.delete_group'),
    (r'^modify_group/(?P<id>\d+)/$', 'auth.views.modify_group'),

    (r'^get_users/$', 'auth.views.users'),
    (r'^add_user/$', 'auth.views.add_user'),

    (r'^get_action_logs/$', 'auth.views.action_logs'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
