#!/bin/bash
# launch flickrfav
#SRCPATH='Favorites/'
SRCPATH='/run/user/1000/gvfs/smb-share:server=tempest,share=flickr/Favorites/'
DSTPATH=$SRCPATH'Download/'
echo $SRCPATH
echo $DSTPATH
./flickrfav.py 63662636@N07 z $SRCPATH $DSTPATH > out.txt
head -2 out.txt 
tail -1 out.txt

