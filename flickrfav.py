#! /usr/bin/env python
from sys import argv
import requests
import os

ENTRIES_PER_PAGE = 100


class CannotDownload(Exception):
    pass


class Flickr(object):
    base_url = 'https://api.flickr.com/services/rest/'
    SKIP = "skip"

    def __init__(self, api_key, user_id):
        self.api_key = api_key
        self.user_id = user_id

        self.ids = {'format': 'json', 'nojsoncallback': '1', }

    @staticmethod
    def find_stored_fav(path):
        """return a set containing the filenames of the images already
        stored locally in path (i.e. previously downloaded).
        Those filenames with a 'z' prefix are stripped of the 'z'.
        Subdirectories are ignored.
        """
        for fav_path, fav_dirs, fav_files in os.walk(path):
            break
        stored_fav = [x.lstrip('z') if x.startswith('z') else x
                        for x in fav_files]
        return set(stored_fav)

    def _getcmd_from_flickr(self, **params):
        """issue a generic get command towards flickr
        and return the json of the response
        """
        # add the basics
        params.update(self.ids)
        # need to pack by hand, and pass a string otherwise
        # the user_id get encoded with %25 instead of @
        payload = '&'.join("%s=%s" % (str(k), str(v)) 
                                for k, v in params.items())
        print "$$$$$", self.base_url, payload
        response = requests.get(self.base_url, params=payload)
        return response.json()

    def get_img_url(self, img_entry):
        photo_id = img_entry['id']
        response = self._getcmd_from_flickr(
                                method='flickr.photos.getInfo',
                                photo_id=photo_id,
                                api_key=self.api_key)
        print "_____", response, "________"
        main_entry = response['photo']
        if main_entry['usage']['candownload'] == 0:
            return self.SKIP

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
            response = fv._getcmd_from_flickr(
                                    method='flickr.favorites.getList',
                                    per_page=ENTRIES_PER_PAGE,
                                    page=cur_page,
                                    user_id=self.user_id,
                                    api_key=self.api_key)
            main_entry = response['photos']
            cur_page = main_entry['page']
            pages = main_entry['pages']
            photos = main_entry['photo']
            page_entries = {img['id']: self.get_img_url(img)
                            for img in photos if img['id'] not in stored_fav}
            all_entries.update(page_entries)
        return all_entries
 
    def download_images(favs, path):
        pass

    def add_new_favorites(self, path):
        """orchestrate the whole thing: retrieve the new fav images
        and save them to the path
        """
        stored_fav = self.find_stored_fav(path)
        print "*** found %d stored favs ***" % len(stored_fav)
        flickr_fav = self.get_current_flickr_fav(stored_fav)
        print "--- %d new favs to fetch ---" % len(flickr_fav)
        self.get_and_save_images(flickr_fav, path)


if __name__ == "__main__":
    if len(argv) < 3:
        print "usage: %s api_key user_id" % (argv[0],)
        exit(1)
    fv = Flickr(argv[1], argv[2])
    FAV_PATH = '/run/user/1000/gvfs/smb-share:server=tempest,share=flickr/Favorites'
    fv.add_new_favorites(FAV_PATH)


