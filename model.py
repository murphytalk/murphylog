# -*- coding: utf-8 -*-
"""Models
Inspired by http://brizzled.clapper.org/id/77
its code is at http://github.com/bmc/picoblog
"""

from google.appengine.ext import db
import logging
import datetime

ENTRIES_PER_PAGE = 10

MONTHS = ('January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'Augest',
          'September',
          'Octobor',
          'November',
          'December')

class Archive(db.Model):
    """
    archives
    """
    date      = db.StringProperty(required=True)  #YYYY-MM
    count     = db.IntegerProperty(required=True,default=0)
    entry_id  = db.IntegerProperty(required=True) #entry id of the newest entry in the given date

    def get_date(self):
        return "%s %s"%(MONTHS[int(self.date[5:7])-1],self.date[0:4])

    @classmethod
    def get_archives(cls):
        q = Archive.gql("ORDER BY date DESC")
        cursor = None
        archives = []
        while True:
            if cursor is not None:
                q.with_cursor(cursor)
            e = q.fetch(100)
            if (e is None) or len(e)==0:
                break
            else:
                for a in e:
                    archives.append(a) #(YYYY-MM,count,newest entry id)
            cursor = q.cursor()
        return archives

    @classmethod
    def update(cls,entry_id,date=None):
        """
        add an entry in date(today if None),update the coresponding archive record
        """
        if date is None:
            date = datetime.date.today()
        ds   = "%04d-%02d"%(date.year,date.month)
        q = Archive.gql('WHERE date = :1',ds)
        e = q.fetch(1)
        if (e is None) or len(e) == 0 :
            #new
            d = Archive(date=ds,count=1,entry_id=entry_id)
        else:
            d = e[0]
            d.count+=1
            d.entry_id = entry_id
        d.put()

class Tag(db.Model):
    """
    Tags
    """
    name    = db.StringProperty (required=True)
    normal  = db.StringProperty (required=True) #normalized name
    count   = db.IntegerProperty(required=True,default=0)

    @property
    def entries(self):
        return Entry.gql("WHERE tags = :1", self.key())

    @classmethod
    def get(cls,key):
        q = db.Query(Tag)
        q.filter('__key__ = ',key)
        obj = q.get()
        return obj

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
    def get_page(cls,get_older_page,tag,bookmark,operator):
        if get_older_page:
            sort = 'DESC'
        else:
            sort = 'ASC'

        if bookmark:
            if tag is None:
                #logging.debug('WHERE entry_id %s %s ORDER BY entry_id %s'%(operator,bookmark,sort))
                q = Entry.gql('WHERE entry_id %s :1 ORDER BY entry_id %s'%(operator,sort), int(bookmark))
            else:
                #logging.debug('WHERE tags = %s AND entry_id %s %s ORDER BY entry_id %s'%(str(tag.key()),operator,bookmark,sort))
                q = Entry.gql('WHERE tags = :1 AND entry_id %s :2 ORDER BY entry_id %s'%(operator,sort),tag,int(bookmark))
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

        if num>=ENTRIES_PER_PAGE:
            e = entries[:ENTRIES_PER_PAGE]
        else:
            e = entries

        if not get_older_page:
            e.reverse()

        return (e,next_page_bkmk,prev_page_bkmk)


    @classmethod
    def get_old_page(cls,tag,bookmark,operator = "<"):
        """
        get next page of entries
        if bookmark has not been set then get from the latest entry

        returns a pair of (results,oldpage_bkmk,newpage_bkmk)
        """
        return Entry.get_page(True,tag,bookmark,operator)

    @classmethod
    def get_new_page(cls,tag,bookmark,operator='>'):
        """
        get previous page of entries
        if bookmark has not been set then get from the latest entry

        returns a pair of (results,newpage_bkmk,oldpage_bkmk)
        """
        return Entry.get_page(False,tag,bookmark,operator)

    @classmethod
    def get_archive_next_page(cls,tag,bookmark,operator = "<="):
        return Entry.get_page(True,None,bookmark,operator)

    @classmethod
    def get(cls,entry_id):
        q = db.Query(Entry)
        q.filter('entry_id = ',int(entry_id))
        return q.get()
