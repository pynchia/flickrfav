#! /usr/bin/env python
from __future__ import unicode_literals
from sys import argv
import requests
import os
import shutil

ENTRIES_PER_PAGE = 100


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
        stored_fav = [x.lstrip('z')[:-4] if x.startswith('z') else x[:-4]
                        for x in fav_files]
        #print "---SSS Stored favs:"
        #for s in stored_fav:
        #    print s
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
        print self.base_url, payload
        response = requests.get(self.base_url, params=payload)
        return response.json()

    def get_img_url(self, img_entry):
        photo_id = img_entry['id']
        response = self._getcmd_from_flickr(
                                method='flickr.photos.getInfo',
                                photo_id=photo_id,
                                api_key=self.api_key)
        #print "_____", response, "________"
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
        
    def get_new_flickr_fav(self, stored_fav):
        """return all my flickr fav
        as a dict = { id1: url1, id2: url2, ... }
        """
        print '---FFF discovering favs'
        cur_page = 0
        pages = -1
        all_entries = {}
        while cur_page != pages:
            cur_page += 1
            response = fv._getcmd_from_flickr(
                                    method='flickr.favorites.getList',
                                    per_page=ENTRIES_PER_PAGE,
                                    page=cur_page,
                                    user_id=self.user_id,
                                    api_key=self.api_key)
            main_entry = response['photos']
            pages = main_entry['pages']
            photos = main_entry['photo']
            #page_entries = {img['id']: self.get_img_url(img)
            #                for img in photos if img['id'] not in stored_fav}
            #all_entries.update(page_entries)
            for img in photos:
                photo_id = img['id']
                if photo_id.encode('utf-8') not in stored_fav:
                    all_entries[photo_id] = self.get_img_url(img)
                    print "NNN new id", photo_id
                else:
                    print ">>> stored already", photo_id
        # print "--- favs stripped of stored:", all_entries
        return all_entries
 
    def download_images(self, favs, dest_path):
        """download the given favorite images from flickr
        skipping the ones lacking permission to do so.
        Return the number of skipped images.
        """
        print '---DDD downloading new favs'
        num_skipped = 0
        for photo_id, url in favs.items():
            if url == self.SKIP:
                print self.SKIP, photo_id
                num_skipped += 1
                continue
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                fname = dest_path+photo_id+url[-4:]
                print fname
                with open(fname, 'wb') as img_file:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, img_file)
        return num_skipped

    def add_new_favorites(self, source_path, dest_path):
        """orchestrate the whole thing: retrieve the new fav images
        and save them to the path
        """
        stored_fav = self.find_stored_fav(source_path)
        print "--- found %d stored favs ***" % len(stored_fav)

        flickr_fav = self.get_new_flickr_fav(stored_fav)
        print "--- %d new favs to fetch ---" % len(flickr_fav)

        num_skipped = self.download_images(flickr_fav, dest_path)
        print "--- skipped %d images due to permission" % num_skipped


if __name__ == "__main__":
    if len(argv) <= 4:
        print "usage: %s api_key user_id sourcepath dest_path" % (argv[0],)
        exit(1)
    fv = Flickr(argv[1], argv[2])
    # FAV_PATH = '/run/user/1000/gvfs/smb-share:server=tempest,share=flickr/Favorites'
    fv.add_new_favorites(argv[3], argv[4])


