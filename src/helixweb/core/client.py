import urllib2
import cjson

from helixweb.core import error_code #@UnresolvedImport


class Client(object):
    def __init__(self, url):
        self.url = url

    def request(self, data):
        try:
            f = urllib2.urlopen(self.url, cjson.encode(data))
            resp = f.read()
            return cjson.decode(resp)
        except urllib2.URLError:
            return {'status': 'error', 'message': 'Service unavailable',
                'code': error_code.HELIX_SERVICE_UNAVAILABLE}

#c = Client('http://localhost:10999')
#resp = c.request({'action': 'ping'})
#print resp