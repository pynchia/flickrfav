A utility to download new favorites from Flickr.
It downloads only the new favs, skipping the ones you have stored locally already. Furthermore, it grabs the images at their original size. In case the owner has disallowed downloading the original, it tries to download the images at a size higher than what Flickr would offer through its API (medium size). Flickr hides the higher sizes behind a different secret_id, which is accessible by browsing a page dedicated to sizes. The utility scrapes the page and locates the new secret_id. It then tries to retrieve the image at 2048px. If it fails, then it tries at 1024px, then it gives up and accepts the standard size.

Usage: ./flickrfav.py user_id prefix source_path dest_path

user_id = the id of the Flickr user whose favorites you want to fetch. It can be yourself or somebody else, I believe.

prefix = the prefix of the filenames stored locally. If you use the images a few at a time, maybe posting them to a FB page, you can mark the ones you have used adding a prefix to their filename.
Example: you source_path contains the files
123456.jpg
246805.jpg
357000.jpg
used468022.jpg
used500021.jpg
Then you can pass the prefix (used) to the utility so that it can match the filenames properly against the image ids on flickr

source_path = the directory where the local images reside

dest_path = the directory where the new fetched images will be saved. It can be the same as source_path.

Have fun!
