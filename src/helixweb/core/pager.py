class Pager(object):

    on_page_ranges = (1, 2, 3, 20, 50, 100, 250)

    def __init__(self, page, total, on_page):
        if on_page in self.on_page_ranges:
            self.on_page = on_page
        else:
            self.on_page = self.on_page_ranges[0]
        self.page = page if page > 0 else 1
        self.total = total

    def update_total(self, helix_resp):
        if 'total' in helix_resp:
            self.total = helix_resp['total']

    def __repr__(self):
        return '%s' % self.__dict__

    @property
    def offset(self):
        return self.on_page * (self.page - 1)

    @property
    def pages_range(self):
        pass