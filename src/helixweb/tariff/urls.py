from django.conf.urls.defaults import patterns


urlpatterns = patterns('',
    (r'^$', 'tariff.views.description'),
)
