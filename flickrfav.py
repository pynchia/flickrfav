#! /usr/bin/env python
from __future__ import unicode_literals
from sys import argv
import requests
import os
import shutil

ENTRIES_PER_PAGE = 100


class FlickrFav(object):
    base_url = 'https://api.flickr.com/services/rest/'

    def __init__(self, api_key, user_id, prefix, source_path, dest_path):
        self.user_id = user_id
        self.prefix = prefix
        self.source_path = source_path
        self.dest_path = dest_path

        # std common params for flickr commands
        self.std_params = {'api_key': api_key,
                           'format': 'json',
                           'nojsoncallback': '1', }

    def _find_stored_favs(self):
        """return a set containing the filenames of the images already
        stored locally in path (i.e. previously downloaded).
        Filenames are stripped of the given prefix if they have one.
        Subdirectories are ignored.
        """
        print "--- find stored favs ---"
        for fav_path, fav_dirs, fav_files in os.walk(self.source_path):
            break
        stored_favs = [x.lstrip(self.prefix)[:-4] for x in fav_files]
        #print "---SSS Stored favs:"
        #for s in stored_fav:
        #    print s
        return set(stored_favs)

    def _getcmd_from_flickr(self, **params):
        """issue a generic get command towards flickr
        and return the json of the response
        """
        # add the standard params
        params.update(self.std_params)
        # need to pack by hand, and pass a string otherwise
        # the user_id gets encoded with %25 instead of @
        payload = '&'.join("%s=%s" % (str(k), str(v)) 
                                for k, v in params.items())
        print self.base_url, payload
        response = requests.get(self.base_url, params=payload)
        return response.json()

    def _get_img_url(self, img_entry):
        photo_id = img_entry['id']
        response = self._getcmd_from_flickr(
                                method='flickr.photos.getInfo',
                                photo_id=photo_id)
        #print "_____", response, "________"
        main_entry = response['photo']
        if main_entry['usage']['candownload'] == 1:
            return "https://farm%s.staticflickr.com/%s/%s_%s_o.%s" % (
                        img_entry['farm'],
                        img_entry['server'],
                        photo_id,
                        main_entry['originalsecret'],
                        main_entry['originalformat'])
        else:
            # original is disallowed, so let's try something else
            base_url4img = 'https://farm%s.staticflickr.com/%s/%s_' % (
                                img_entry['farm'],
                                img_entry['server'],
                                photo_id)
            img_path_alias = main_entry['owner']['path_alias']
            url4sizes = 'https://www.flickr.com/photos/%s/%s/sizes/k/' % (
                    img_path_alias,
                    photo_id)
            print "*** Original disallowed, try k size (2048px)", url4sizes
            response = requests.get(url4sizes)
            if response.status_code == 200:
                # flickr gives a page with the highest available size
                # look for the url of the image in the page
                __, _, tail = response.text.partition(base_url4img)
                #ignore the first one, get the second match
                __, _, tail = tail.partition(base_url4img)
                #print "tail=", tail.encode('utf-8)
                very_secret_suffix = '_k.jpg'
                very_secret_len = tail.find(very_secret_suffix)
                if very_secret_len == -1:
                    # it's not a k size, try with the b size (1024px)
                    print "*** no k size, try b size (1024px)"
                    very_secret_suffix = '_b.jpg'
                    very_secret_len = tail.find(very_secret_suffix)
                    if very_secret_len == -1:
                        print "*** no b size available either"

                # extract the very_secret
                #print "very_secret_pos=", very_secret_pos
                if very_secret_len >= 0:
                    very_secret = tail[:very_secret_len]
                    #print "UUU"
                    #print base_url4img
                    #print very_secret.encode('utf-8')
                    #print very_secret
                    #print very_secret_suffix
                    return base_url4img+very_secret+very_secret_suffix
            else:
                print "ERROR getting the sizes page", photo_id

            # nothing works, so fall back to the std plain image format
            print "*** fall back to std size, whatever it is"
            return base_url4img+main_entry['secret']+'.jpg'

    def _get_new_flickr_favs(self, stored_fav):
        """return all my flickr fav
        as a dict = { id1: url1, id2: url2, ... }
        skipping the ones which have been stored (i.e. downloaded already)
        and the ones which are protected by flickr (i.e. download not perm.)
        """
        print '--- discovering favs'
        cur_page = 0
        pages = -1
        new_favs = {}
        while cur_page != pages:
            cur_page += 1
            response = self._getcmd_from_flickr(
                                    method='flickr.favorites.getList',
                                    per_page=ENTRIES_PER_PAGE,
                                    page=cur_page,
                                    user_id=self.user_id)
            main_entry = response['photos']
            pages = main_entry['pages']
            photos = main_entry['photo']
            for img in photos:
                photo_id = img['id']
                if photo_id.encode('utf-8') not in stored_fav:
                    url = self._get_img_url(img)
                    new_favs[photo_id] = url
                #    print "NNN new id", photo_id
                #else:
                #    print photo_id, "stored already"
        return new_favs
 
    def _download_images(self, favs):
        """download the given favorite images from flickr
        skipping the ones lacking permission to do so.
        Return the number of skipped images.
        """
        print '--- downloading new favs'
        num_downloaded = 0
        num_errors = 0
        for photo_id, url in favs.items():
            print url
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                fname = self.dest_path+photo_id+url[-4:]
                #print fname
                with open(fname, 'wb') as img_file:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, img_file)
                num_downloaded += 1
            else:
                print "ERROR bad response from flickr:", response.status_code
                num_errors += 1
        return num_downloaded, num_errors

    def add_new_favorites(self):
        """Orchestrate the whole process:
        a) find the stored favorites
        b) retrieve the new favorites
        c) save them to the path
        """
        stored_favs = self._find_stored_favs()
        print "*** %d stored favs found" % len(stored_favs)

        new_favs = self._get_new_flickr_favs(stored_favs)
        print "*** %d new favs" % len(new_favs)

        num_downloaded, num_errors = self._download_images(new_favs)
        print "*** %d images downloaded, %d errors" % (
                                        num_downloaded,
                                        num_errors)

if __name__ == "__main__":
    if len(argv) <= 5:
        print "usage: %s api_key user_id prefix sourcepath dest_path" % (argv[0],)
        exit(1)
    ff = FlickrFav(api_key=argv[1],
                   user_id=argv[2],
                   prefix=argv[3],
                   source_path=argv[4],
                   dest_path=argv[5])
    ff.add_new_favorites()

