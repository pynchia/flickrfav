#! /usr/bin/env python
from sys import argv
import requests
# import os


class Flickr(object):
    base_url = 'https://api.flickr.com/services/rest/'

    def __init__(self, api_key, user_id):
        self.ids = {'api_key': api_key,
                    'user_id': user_id,
                    'format': 'json',
                    'nojsoncallback': '1'
                   }

#    def encode_call(self, method, **params):
#        url = self.base_url+method
#        url += '&api_key=%s&user_id=%s' % (self.api_key, self.user_id)
#        for p,v in params.items():
#            url += '&%s=%s' % (p, v)
#        url += '&format=json&nojsoncallback=1'
#        return url
    def get(self, **params):
        params.update(self.ids)
        payload='&'.join("%s=%s" % (k,v) for k,v in params.items())
        r = requests.get(self.base_url, params=payload)
        return r

if __name__ == "__main__":
    if len(argv) < 3:
        print "usage: %s api_key user_id" % (argv[0],)
        exit(1)
    fv = Flickr(argv[1], argv[2])
    fav_response = fv.get(method='flickr.favorites.getList', per_page=500)
    print "url=", fav_response.url
    print "Status code=", fav_response.status_code
    print fav_response.text
#    print fav_response.json()


