#! /usr/bin/env python
from sys import argv
import requests
import os

FAV_PATH = '/run/user/1000/gvfs/smb-share:server=tempest,share=flickr/Favorites'
ENTRIES_PER_PAGE = 100

class Flickr(object):
    base_url = 'https://api.flickr.com/services/rest/'

    def __init__(self, api_key, user_id):
        self.ids = {'api_key': api_key,
                    'user_id': user_id,
                    'format': 'json',
                    'nojsoncallback': '1'
                   }

    @staticmethod
    def find_stored_fav(path):
        """return a set containing the filenames of the images already
        stored locally in path (i.e. previously downloaded).
        Those filenames with a 'z' prefix are stripped of the 'z'.
        Subdirectories are ignored.
        """
        fav_path, fav_dirs, fav_files = os.walk(path)[0]
        fav_in_stock = set(
                    map(lambda x: x.lstrip('z') if x.startswith('z') else x,
                        fav_files))
        return fav_in_stock

    def get_from_flickr(self, **params):
        """issue the get command towards flickr
        """
        # add the basics
        params.update(self.ids)
        # need to pack by hand, and pass a string otherwise
        # the user_id get encoded with %25 instead of @
        payload = '&'.join("%s=%s" % (k, v) for k, v in params.items())
        response = requests.get(self.base_url, params=payload)
        return response

    def get_img_url(img_entry):
        photo_id = img_entry['id']
        response = fv.get_from_flickr(
                                method='flickr.favorites.getInfo',
                                photo_id=photo_id)
        main_entry = response['photo']
        o_secret = main_entry['originalsecret']
        o_format = main_entry['originalformat']
        
        return "https://farm%s.staticflickr.com/%s/%s_%s_o.%s" % (
                    img_entry['farm'],
                    img_entry['server'],
                    photo_id,
                    o_secret,
                    o_format
                 )
    
    def get_current_flickr_fav(self, stored_fav):
        """return all my flickr fav
        as a dict = { id1: url1, id2: url2, ... }
        """
        cur_page = '1'
        pages = 'X'
        all_entries = {}
        while cur_page != pages:
            response = fv.get_from_flickr(
                                    method='flickr.favorites.getList',
                                    per_page=ENTRIES_PER_PAGE,
                                    page=cur_page)
            main_entry = response['photos']
            cur_page = main_entry['page']
            pages = main_entry['pages']
            photos = main_entry['photo']
            page_entries = {img['id']: self.get_img_url(img)
                                                for img in photos}
            all_entries.update(page_entries)
        return all_entries
 
    def deduct_stored_fav(json_response, stored_fav):
        """return the list of those images not downloaded yet
        """
        main_entry = json_response['photos']
        

if __name__ == "__main__":
    if len(argv) < 3:
        print "usage: %s api_key user_id" % (argv[0],)
        exit(1)
    fv = Flickr(argv[1], argv[2])

    print "url=", fav_response.url
    print "Status code=", fav_response.status_code
#    print fav_response.text
    json = fav_response.json()


