# -*- coding: utf-8 -*-
"""Models
Inspired by http://brizzled.clapper.org/id/77
its code is at http://github.com/bmc/picoblog
"""

from google.appengine.ext import db
import logging

ENTRIES_PER_PAGE = 10

class Tag(db.Model):
    """
    Tags
    """
    name    = db.StringProperty (required=True)
    count   = db.IntegerProperty(required=True,default=0)

class Entry(db.Model):
    """
    Blog entry class

    provide some class function to manipulate quries and results
    """
    #title   = db.StringProperty(required=True,default="x")
    title   = db.StringProperty(required=False)
    subject = db.TextProperty()
    text    = db.TextProperty()
    owner   = db.UserProperty(auto_current_user_add=True)
    private = db.BooleanProperty(required=True, default=False)
    format  = db.StringProperty(required=True, default="rs",choices=set(["rs", "st", "bb"]),indexed=False)

    post_time = db.DateTimeProperty(auto_now_add=True)
    last_edit = db.DateTimeProperty(auto_now_add=True)


    #tags = db.ListProperty(db.Category)
    tags = db.ReferenceProperty(Tag)
    #id = db.StringProperty()

    @classmethod
    def get_next_page(cls,bookmark):
        """
        get next page of entries
        if bookmark has not been set then get from the latest entry

        returns a pair of (results,bookmark)
        """
        q = Entry.gql('ORDER BY __key__ DESC')
        if bookmark:
            bookmark_key = db.Key(bookmark)
            q = Entry.gql('WHERE __key__ < :1 ORDER BY __key__ DESC', bookmark_key)

        entries = q.fetch(ENTRIES_PER_PAGE+1)
        new_bookmark = None
        if len(entries)==ENTRIES_PER_PAGE+1:
            new_bookmark=str(entries[ENTRIES_PER_PAGE-1].key())

        return (entries[:ENTRIES_PER_PAGE],new_bookmark)

    @classmethod
    def get(cls,key):
        q = db.Query(Entry)
        q.filter('__key__ = ', db.Key(key))
        return q.get()
