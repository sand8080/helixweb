class Pager(object):

    on_page_ranges = (1, 2, 3, 20, 50, 100, 250)

    def __init__(self, offset, total, on_page):
        on_page = self._get_int_val(on_page)
        self.on_page = on_page if on_page in self.on_page_ranges else self.on_page_ranges[0]
        self.offset = self._get_int_val(offset)
        self.total = self._get_int_val(total)

    def _get_int_val(self, val):
        try:
            val = int(val)
        except (ValueError, TypeError):
            val = 0
        return val

    def update_total(self, helix_resp):
        self.total = helix_resp.get('total', 0)

    def __repr__(self):
        return '%s' % self.__dict__

    @property
    def page(self):
        return int(self.offset / self.on_page) + 1

    @property
    def pages_range(self):
        p_num = 3
        pages = range(self.page - p_num, self.page + p_num + 1)
        pages = filter(lambda x: x > 0 and (x - 1) * self.on_page < self.total, pages)
        res = [(p, (p - 1) * self.on_page) for p in pages]

        # adding ... in list head and tail
        cur_page_idx = pages.index(self.page)
        if len(pages) - cur_page_idx >= p_num:
            (_, p_offset) = res[-1]
            res[-1] = ('...', p_offset)
        if cur_page_idx >= p_num:
            (_, p_offset) = res[0]
            res[0] = ('...', p_offset)
        return res
