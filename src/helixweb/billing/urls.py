from django.conf.urls.defaults import patterns


urlpatterns = patterns('',
    (r'^$', 'billing.views.description'),

    (r'^get_used_currencies/$', 'billing.views.used_currencies'),
    (r'^modify_used_currencies/$', 'billing.views.modify_used_currencies'),

    (r'^user_info/(?P<id>\d+)/$', 'billing.views.user_info'),

    (r'^get_balances/$', 'billing.views.balances'),
    (r'^get_balances/(?P<user_id>\d+)/$', 'billing.views.user_balances'),
    (r'^add_balance/$', 'billing.views.add_balance'),

    (r'^get_action_logs/$', 'billing.views.action_logs'),

    (r'^get_balances_self/$', 'billing.views.balances_self'),
    (r'^get_action_logs_self/$', 'billing.views.action_logs_self'),
)
