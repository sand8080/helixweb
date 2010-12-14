class Pager(object):

    on_page_ranges = (2, 20, 50, 100, 250)

    def __init__(self, offset, total, on_page):
        self.on_page = self._aligned_on_page(self._get_int_val(on_page))
        self.offset = self._aligned_offset(self._get_int_val(offset))
        self.total = self._get_int_val(total)

    def _get_int_val(self, val):
        try:
            val = int(val)
        except (ValueError, TypeError):
            val = 0
        return val

    def _aligned_on_page(self, on_page):
        if on_page not in self.on_page_ranges:
            return self.on_page_ranges[0]
        else:
            return on_page

    def _aligned_offset(self, offset):
        return int(offset / self.on_page) * self.on_page

    def last_page(self):
        page_num = int(self.total / self.on_page)
        if page_num and (self.total % self.on_page) == 0:
            page_num -= 1
        return page_num + 1

    def last_page_offset(self):
        return (self.last_page() - 1) * self.on_page

    def update_total(self, helix_resp):
        self.total = helix_resp.get('total', 0)

    def __repr__(self):
        return '%s' % self.__dict__

    def current_page(self):
        return int(self.offset / self.on_page) + 1

    def pages_range(self):
        p_num = 3
        cur_page = self.current_page()
        pages = range(cur_page - p_num, cur_page + p_num + 1)
        pages = filter(lambda x: x > 0 and (x - 1) * self.on_page < self.total, pages)
        res = [(p, (p - 1) * self.on_page) for p in pages]

        # adding ... in list head and tail
        try:
            cur_page_idx = pages.index(cur_page)
            if len(pages) - cur_page_idx >= p_num:
                (_, p_offset) = res[-1]
                res[-1] = ('...', p_offset)
            if cur_page_idx >= p_num:
                (_, p_offset) = res[0]
                res[0] = ('...', p_offset)
        except ValueError:
            # page not in list
            pass
        return res
