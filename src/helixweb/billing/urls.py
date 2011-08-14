from django.conf.urls.defaults import patterns


urlpatterns = patterns('',
    (r'^$', 'billing.views.description'),

    # system wide operations
    (r'^get_used_currencies/$', 'billing.views.used_currencies'),
    (r'^modify_used_currencies/$', 'billing.views.modify_used_currencies'),

    (r'^add_balance/$', 'billing.views.add_balance'),
    (r'^get_balances/$', 'billing.views.balances'),
    (r'^get_transactions/$', 'billing.views.transactions'),
    (r'^get_locks/$', 'billing.views.locks'),
    (r'^get_action_logs/$', 'billing.views.action_logs'),

    # user scoped operations
    (r'^user_info/(?P<id>\d+)/$', 'billing.views.user_info'),

    (r'^add_balance/(?P<user_id>\d+)/$', 'billing.views.user_add_balance'),
    (r'^modify_balances/(?P<balance_id>\d+)/$', 'billing.views.modify_balance'),
    (r'^modify_balances/(?P<user_id>\d+)/(?P<balance_id>\d+)/$',
        'billing.views.user_modify_balance'),
    (r'^get_balances/(?P<user_id>\d+)/$', 'billing.views.user_balances'),

    (r'^add_receipt/(?P<user_id>\d+)/(?P<balance_id>\d+)/$',
        'billing.views.user_add_receipt'),
    (r'^add_bonus/(?P<user_id>\d+)/(?P<balance_id>\d+)/$',
        'billing.views.user_add_bonus'),
    (r'^lock/(?P<user_id>\d+)/(?P<balance_id>\d+)/$',
        'billing.views.user_lock'),
    (r'^lock/(?P<user_id>\d+)/$',
        'billing.views.user_lock'),
    (r'^unlock/$', 'billing.views.unlock'),
    (r'^charge_off/$', 'billing.views.charge_off'),
    (r'^get_locks/(?P<user_id>\d+)/(?P<balance_id>\d+)/$',
        'billing.views.user_balance_locks'),
    (r'^get_transactions/(?P<user_id>\d+)/(?P<balance_id>\d+)/$',
        'billing.views.user_transactions'),

    (r'^get_action_logs/(?P<user_id>\d+)/$', 'billing.views.user_action_logs'),

    # self operations
    (r'^get_balances_self/$', 'billing.views.balances_self'),
    (r'^get_transactions_self/$', 'billing.views.transactions_self'),
    (r'^get_locks_self/$', 'billing.views.locks_self'),
    (r'^get_action_logs_self/$', 'billing.views.action_logs_self'),
)
