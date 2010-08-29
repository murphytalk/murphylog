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
    entry_id = db.IntegerProperty(required=True)
    title    = db.StringProperty(required=False)
    subject  = db.TextProperty()
    text     = db.TextProperty()
    owner    = db.UserProperty(auto_current_user_add=True)
    private  = db.BooleanProperty(required=True, default=False)
    format   = db.StringProperty(required=True, default="rs",choices=set(["rs", "st", "bb"]),indexed=False)

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
    def get_page(cls,get_older_page,tag,bookmark,operator,no_revers):
        if get_older_page:
            sort = 'DESC'
        else:
            sort = 'ASC'

        if bookmark:
            if tag is None:
                q = Entry.gql('WHERE entry_id %s :1 ORDER BY entry_id %s'%(operator,sort), int(bookmark))
            else:
                q = Entry.gql('WHERE tags = :1 AND entry_id %s :2 ORDER BY entry_id %s'%(operator,sort),tag,bookmark)
        else:
            if tag is None:
                q = Entry.gql('ORDER BY entry_id %s'%sort)
            else:
                q = Entry.gql('WHERE tags = :1 ORDER BY entry_id %s'%sort,tag)

        entries = q.fetch(ENTRIES_PER_PAGE+1)

        next_page_bkmk = prev_page_bkmk = None

        if bookmark:
            #bookmark is not None means it is switched from last page
            #so save the first(newest if get_older_page==False) entry of this page as bookmark to seek to previous page
            prev_page_bkmk = str(entries[0].entry_id)

        num = len(entries)

        if num == ENTRIES_PER_PAGE+1:
            next_page_bkmk=str(entries[ENTRIES_PER_PAGE-1].entry_id)
        elif num<ENTRIES_PER_PAGE and num > 0:
            if no_reverse:
                return (None,None,None)
            else:
                #less than ENTRIES_PER_PAGE entries left on next page
                #we use the last entry to seek back untill we have  ENTRIES_PER_PAGE entries
                #need to set the 3rd parameter no_reverse to True
                #otherwise there will be a infinite recursion if the total num is less than ENTRIES_PER_PAGE
                if get_older_page:
                    op = ">=" #we need to include the last entry so need = here
                else:
                    op = "<="
                e,bk1,bk2 = Entry.get_page(not get_older_page,tag,str(entries[-1].entry_id),op,True)
                if e is not None:
                    entries      = e
                    newpage_bkmk = bk1

        if num>=ENTRIES_PER_PAGE:
            e = entries[:ENTRIES_PER_PAGE]

        if not get_older_page:
            e.reverse()

        return (e,next_page_bkmk,prev_page_bkmk)


    @classmethod
    def get_old_page(cls,tag,bookmark,operator = "<", no_reverse = False):
        """
        get next page of entries
        if bookmark has not been set then get from the latest entry

        returns a pair of (results,oldpage_bkmk,newpage_bkmk)
        """
        return Entry.get_page(True,tag,bookmark,operator,no_reverse)

    @classmethod
    def get_new_page(cls,tag,bookmark,operator='>',no_reverse=False):
        """
        get previous page of entries
        if bookmark has not been set then get from the latest entry

        returns a pair of (results,newpage_bkmk,oldpage_bkmk)
        """
        return Entry.get_page(False,tag,bookmark,operator,no_reverse)

    @classmethod
    def get(cls,entry_id):
        q = db.Query(Entry)
        q.filter('entry_id = ',int(entry_id))
        return q.get()
