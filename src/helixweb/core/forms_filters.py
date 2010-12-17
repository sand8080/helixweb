from helixweb.core.pager import Pager


class FilterForm(object):
    def __init__(self, *args, **kwargs):
        self.pager = self._get_pager(kwargs['request'])
        super(FilterForm, self).__init__(*args, **kwargs)

    def _get_pager(self, request):
        on_page = request.COOKIES.get('pager_on_page', 0)
        total = request.GET.get('pager_total', None)
        offset = request.GET.get('pager_offset', 0)
        return Pager(offset, total, on_page)

    def as_helix_request(self):
        f_params = dict(self.cleaned_data)
        d = super(FilterForm, self).as_helix_request()
        for k in f_params.keys():
            del d[k]
        d['filter_params'] = f_params
        d['paging_params'] = {'limit': self.pager.on_page,
            'offset': self.pager.offset}
        return d

    def update_total(self, helix_resp):
        self.pager.update_total(helix_resp)
