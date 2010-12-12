from helixweb.core.pager import Pager


class FilterForm(object):
    def __init__(self, *args, **kwargs):
        self.pager = self._get_pager(kwargs['request'])
        super(FilterForm, self).__init__(*args, **kwargs)

    def _get_pager(self, request):
        try:
            on_page = int(request.COOKIES.get('pager_on_page', 0))
        except ValueError:
            on_page = 0
        total = request.GET.get('pager_total', None)
        page = request.GET.get('pager_page', 1)
        return Pager(page, total, on_page)

    def _get_cleaned_data(self):
        f_params = dict(self.cleaned_data)
        d = super(FilterForm, self)._get_cleaned_data()
        for k in f_params.keys():
            del d[k]
        d['filter_params'] = f_params
        d['paging_params'] = {'limit': self.pager.on_page,
            'offset': self.pager.offset}
        return d

    def request(self):
        resp = super(FilterForm, self).request()
        self.pager.update_total(resp)
        return resp