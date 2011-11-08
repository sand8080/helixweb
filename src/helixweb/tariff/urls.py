from django.conf.urls.defaults import patterns


urlpatterns = patterns('',
    # system wide operations
    (r'^$', 'tariff.views.description'),
    (r'^add_tariffication_object/$', 'tariff.views.add_tariffication_object'),
    (r'^get_tariffication_objects/$', 'tariff.views.get_tariffication_objects'),
    (r'^modify_tariffication_object/(?P<to_id>\d+)/$', 'tariff.views.modify_tariffication_object'),
    (r'^delete_tariffication_object/(?P<to_id>\d+)/$', 'tariff.views.delete_tariffication_object'),

)
