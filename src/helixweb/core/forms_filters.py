from helixweb.core.pager import Pager
class FilterForm(object):
    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.pager = self._get_pager(args[0])

    def _get_pager(self, data):
        try:
            on_page = int(data.COOKIES.get('pager_on_page', 0))
        except ValueError:
            on_page = 0
        total = data.get('pager_total', None)
        offset = data.get('pager_offset', None)
        return Pager(offset, total, on_page)



    def _get_cleaned_data(self):
        f_params = dict(self.cleaned_data)
        d = super(FilterForm, self)._get_cleaned_data()
        for k in f_params.keys():
            del d[k]
        d['filter_params'] = f_params
        d['paging_params'] = {}
        return d
