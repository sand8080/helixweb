import urllib2
import cjson


class Client(object):
    def __init__(self, url):
        self.url = url

    def request(self, data):
        try:
            f = urllib2.urlopen(self.url, cjson.encode(data))
            resp = f.read()
            return cjson.decode(resp)
        except urllib2.URLError:
            return 'Service unavailable'
