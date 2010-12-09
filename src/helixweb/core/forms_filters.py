class FilterForm(object):
    def _get_cleaned_data(self):
        f_params = dict(self.cleaned_data)
        d = super(FilterForm, self)._get_cleaned_data()
        for k in f_params.keys():
            del d[k]
        d['filter_params'] = f_params
        d['paging_params'] = {}
        return d