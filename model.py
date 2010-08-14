# -*- coding: utf-8 -*-
"""Models
Inspired by http://brizzled.clapper.org/id/77
its code is at http://github.com/bmc/picoblog
"""

from google.appengine.ext import db
import logging
import datetime

ENTRIES_PER_PAGE = 10

class Tag(db.Model):
    """
    Tags
    """
    name    = db.StringProperty (required=True)
    count   = db.IntegerProperty(required=True,default=0)

    @property
    def entries(self):
        return Entry.gql("WHERE tags = :1", self.key())

    @classmethod
    def get(cls,key):
        q = db.Query(Tag)
        q.filter('__key__ = ',key)
        return q.get()

ZERO  = datetime.timedelta(0)
TOKYO = datetime.timedelta(hours=9)

class UTC(datetime.tzinfo):
    """UTC"""
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

class MyTimeZone(datetime.tzinfo):
    def utcoffset(self, dt):
        return TOKYO
    def dst(self, dt):
        return ZERO
    def tzname(self, dt):
        return "GMT+9"


class Entry(db.Model):
    """
    Blog entry class

    provide some class function to manipulate quries and results
    """
    title   = db.StringProperty(required=False)
    subject = db.TextProperty()
    text    = db.TextProperty()
    owner   = db.UserProperty(auto_current_user_add=True)
    private = db.BooleanProperty(required=True, default=False)
    format  = db.StringProperty(required=True, default="rs",choices=set(["rs", "st", "bb"]),indexed=False)

    post_time = db.DateTimeProperty(auto_now_add=True)
    last_edit = db.DateTimeProperty(auto_now_add=True)

    tags = db.ListProperty(db.Key)

#    def __str__(self):
#        return self.title

    def get_tags_as_str(self):
        tags=""
        for tk in self.tags:
            tag = Tag.get(tk)
            tags="%s %s"%(tags,tag.name)
        return tags

    def get_tags(self):
        tags = []
        for tk in self.tags:
            tags.append( Tag.get(tk) )
        return tags


    def get_post_time(self):
        return self.post_time.replace(tzinfo=UTC()).astimezone(MyTimeZone())

    def get_ledit_time(self):
        return self.last_edit.replace(tzinfo=UTC()).astimezone(MyTimeZone())

    @classmethod
    def get_old_page(cls,tag,bookmark,operator = "<", no_reverse = False):
        """
        get next page of entries
        if bookmark has not been set then get from the latest entry

        returns a pair of (results,oldpage_bkmk,newpage_bkmk)
        """
        if bookmark:
            bookmark_key = db.Key(bookmark)
            if tag is None:
                q = Entry.gql('WHERE __key__ %s :1 ORDER BY __key__ DESC'%(operator), bookmark_key)
            else:
                q = Entry.gql('WHERE tags = :1 AND __key__ %s :2 ORDER BY __key__ DESC'%(operator),tag,bookmark_key)
        else:
            if tag is None:
                q = Entry.gql('ORDER BY __key__ DESC')
            else:
                q = Entry.gql('WHERE tags = :1 ORDER BY __key__ DESC',tag)

        entries = q.fetch(ENTRIES_PER_PAGE+1)

        oldpage_bkmk = newpage_bkmk = None
        if bookmark:
            #bookmark is not None means it is switched from newer page
            #so save the first(newest) entry of this page as bookmark to seek to newer page
            newpage_bkmk = str(entries[0].key())

        num = len(entries)

        if num == ENTRIES_PER_PAGE+1:
            oldpage_bkmk=str(entries[ENTRIES_PER_PAGE-1].key())
        elif num<ENTRIES_PER_PAGE and num > 0:
            if no_reverse:
                return (None,None,None)
            else:
                #less than ENTRIES_PER_PAGE entries left on next page
                #we use the last entry to seek back untill we have  ENTRIES_PER_PAGE entries
                #need to set the 3rd parameter no_reverse to True
                #otherwise there will be a infinite recursion if the total num is less than ENTRIES_PER_PAGE
                 e,bk1,bk2 = Entry.get_new_page(tag,str(entries[-1].key()),">=",True)
                 if e is not None:
                     entries      = e
                     newpage_bkmk = bk1

        return (entries[:ENTRIES_PER_PAGE],oldpage_bkmk,newpage_bkmk)

    @classmethod
    def get_new_page(cls,tag,bookmark,operator='>',no_reverse=False):
        """
        get previous page of entries
        if bookmark has not been set then get from the latest entry

        returns a pair of (results,newpage_bkmk,oldpage_bkmk)
        """
        logging.info("new page,tag=%s,bkmk=%s"%(tag,bookmark))
        if bookmark:
            bookmark_key = db.Key(bookmark)
            if tag is None:
                q = Entry.gql('WHERE __key__ %s :1 ORDER BY __key__ ASC'%(operator), bookmark_key)
            else:
                q = Entry.gql('WHERE tags = :1 AND __key__ %s :2 ORDER BY __key__ ASC'%(operator),tag,bookmark_key)

        else:
            if tag is None:
                q = Entry.gql('ORDER BY __key__ ASC')
            else:
                q = Entry.gql('WHERE tags = :1 ORDER BY __key__ ASC',tag)

        entries = q.fetch(ENTRIES_PER_PAGE+1)

        oldpage_bkmk = newpage_bkmk = None

        if bookmark:
            oldpage_bkmk = str(entries[0].key())

        num = len(entries)

        if num==ENTRIES_PER_PAGE+1:
            newpage_bkmk = str(entries[ENTRIES_PER_PAGE-1].key())
        elif num<ENTRIES_PER_PAGE and num>0:
            if no_reverse:
                return (None,None,None)
            else:
                 e2,bk1,bk2 = Entry.get_old_page(tag,str(entries[0].key()),"<=",True)
                 if e2 is not None:
                     e            = e2
                     oldpage_bkmk = bk1

        if num>=ENTRIES_PER_PAGE:
            e = entries[:ENTRIES_PER_PAGE]
            e.reverse()

        return (e,newpage_bkmk,oldpage_bkmk)

    @classmethod
    def get(cls,key):
        q = db.Query(Entry)
        q.filter('__key__ = ', db.Key(key))
        return q.get()
