import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _
from helixweb.auth.widgets import ServicesWidget


class MonthYearWidget(forms.MultiWidget):
    """
    A widget that splits a date into Month/Year with selects.
    """
    def __init__(self, attrs=None):
        months = (
            ('01', 'Jan (01)'),
            ('02', 'Feb (02)'),
            ('03', 'Mar (03)'),
            ('04', 'Apr (04)'),
            ('05', 'May (05)'),
            ('06', 'Jun (06)'),
            ('07', 'Jul (07)'),
            ('08', 'Aug (08)'),
            ('09', 'Sep (09)'),
            ('10', 'Oct (10)'),
            ('11', 'Nov (11)'),
            ('12', 'Dec (12)'),
        )

        year = int(datetime.date.today().year)
        year_digits = range(year, year+10)
        years = [(year, year) for year in year_digits]

        widgets = (forms.Select(attrs=attrs, choices=months), forms.Select(attrs=attrs, choices=years))
        super(MonthYearWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.month, value.year]
        return [None, None]

    def render(self, name, value, attrs=None):
        try:
            value = datetime.date(month=int(value[0]), year=int(value[1]), day=1)
        except:
            value = ''

        return super(MonthYearWidget, self).render(name, value, attrs)


class MonthYearField(forms.MultiValueField):
    def compress(self, data_list):
        if data_list:
            return datetime.date(year=int(data_list[1]), month=int(data_list[0]), day=1)
        return datetime.date.today()


#class ServicesField(forms.MultiValueField):
#    def __init__(self, services, *args, **kwargs):
##        fields = ([forms.CharField(label=_('service name'), max_length=32, widget=ServicesWidget) for s in services])
#        fields = (
#            forms.CharField(label=_('service name'), max_length=32),
#            forms.CharField(label=_('service name'), max_length=32),
#        )
#        super(ServicesField, self).__init__(fields, *args, **kwargs)
#
#    def compress(self, data_list):
#        if data_list:
#            return data_list
#        return None