import urllib2
import cjson

from helixweb.core import error_code #@UnresolvedImport
from helixweb.error import UnauthorizedActivity


class Client(object):
    def __init__(self, url):
        self.url = url

    def notchecked_request(self, data):
        try:
            f = urllib2.urlopen(self.url, cjson.encode(data))
            resp = f.read()
            return cjson.decode(resp)
        except urllib2.URLError:
            return {'status': 'error', 'message': 'Service unavailable',
                'code': error_code.HELIX_SERVICE_UNAVAILABLE}

    def request(self, data):
        resp = self.notchecked_request(data)
        self._check_response(resp)
        return resp

    def _check_response(self, resp):
        unauth = ('HELIXAUTH_SESSION_NOT_FOUND', 'HELIXAUTH_SESSION_EXPIRED',
            'HELIXAUTH_USER_AUTH_ERROR')
        if resp['status'] != 'ok' and resp['code'] in unauth:
            raise UnauthorizedActivity


#c = Client('http://localhost:10999')
#resp = c.request({'action': 'ping'})
#print resp