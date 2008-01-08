#!/usr/bin/python

import sys

FROG_PKG="FromFrog"

if FROG_PKG not in sys.path: 
    sys.path.append(FROG_PKG)

import frog.objects
import frog.xmlstorage.objects as storageobjects
StorageEngine=storageobjects.XMLStorageEngine

class Loader:
    def __init__(self,blogdata_dir,username):
        self.blogdata = blogdata_dir
        self.username = username
        self.engine   = StorageEngine(None, (blogdata_dir,username))

    def list_all(self):
        """
        list all blog entries as [(date,id),]
        """
        return self.engine.listAllBlogEntries()

    def load_entry(self,datestr,id):
        return frog.objects.BlogEntry.load(self.engine,datestr,id)

if __name__=="__main__":
    blogdata="/home/BACKUP/FrogBlog/blogdata"
    username="murphytalk"
    loader=Loader(blogdata,username)
    all=loader.list_all()
    all.reverse()
    print '%d articles loaded'%len(all)
    for datestr,id in all:
        entry=loader.load_entry(datestr,id)
        print entry.datetime


