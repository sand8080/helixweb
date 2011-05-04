from django.conf.urls.defaults import patterns


urlpatterns = patterns('',
    (r'^$', 'billing.views.description'),

    (r'^get_used_currencies/$', 'billing.views.used_currencies'),
    (r'^modify_used_currencies/$', 'billing.views.modify_used_currencies'),

    (r'^get_balances/$', 'billing.views.balances'),

    (r'^get_balance_self/$', 'billing.views.balance_self'),

    (r'^get_action_logs_self/$', 'billing.views.action_logs_self'),
    (r'^get_action_logs/$', 'billing.views.action_logs'),
)
