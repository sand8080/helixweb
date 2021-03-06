from django.conf.urls import patterns


urlpatterns = patterns('',
    (r'^$', 'auth.views.description'),

    (r'^login/(?P<env_name>[\w|\W]+)', 'auth.views.login_env'),
    (r'^login/', 'auth.views.login'),

    (r'^logout/', 'auth.views.logout'),

    (r'^register_user/(?P<env_name>[\w|\W]+)', 'auth.views.register_user_env'),
    (r'^register_user/', 'auth.views.register_user'),

    (r'^restore_password/(?P<env_name>[\w|\W]+)', 'auth.views.restore_password_env'),
    (r'^restore_password/', 'auth.views.restore_password'),

    (r'^add_environment/$', 'auth.views.add_environment'),
    (r'^modify_environment/$', 'auth.views.modify_environment'),

    (r'^user_info/(?P<id>\d+)/$', 'auth.views.user_info'),
    (r'^modify_users/(?P<id>\d+)/$', 'auth.views.modify_user'),
    (r'^get_action_logs/(?P<id>\d+)/$', 'auth.views.user_action_logs'),
    (r'^modify_user_self/$', 'auth.views.modify_user_self'),
    (r'^get_action_logs_self/$', 'auth.views.action_logs_self'),

    (r'^get_services/$', 'auth.views.services'),
    (r'^add_service/$', 'auth.views.add_service'),
    (r'^delete_service/(?P<id>\d+)/$', 'auth.views.delete_service'),
    (r'^modify_service/(?P<id>\d+)/$', 'auth.views.modify_service'),

    (r'^get_groups/$', 'auth.views.groups'),
    (r'^add_group/$', 'auth.views.add_group'),
    (r'^delete_group/(?P<id>\d+)/$', 'auth.views.delete_group'),
    (r'^modify_group/(?P<id>\d+)/$', 'auth.views.modify_group'),

    (r'^get_users/$', 'auth.views.users'),
    (r'^add_user/$', 'auth.views.add_user'),

    (r'^get_notifications/$', 'auth.views.notifications'),
    (r'^modify_notifications/(?P<id>\d+)/$', 'auth.views.modify_notifications'),

    (r'^get_action_logs/$', 'auth.views.action_logs'),

    (r'^get_api_scheme/$', 'auth.views.api_scheme'),
)
