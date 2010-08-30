# -*- coding: utf-8 -*-
# coding=utf-8
import os.path

from google.appengine.ext        import webapp
from google.appengine.ext.webapp import template
from google.appengine.api        import users
from google.appengine.api        import datastore_errors

#from mytwitter import get_my_tweets,get_my_twitter_profile

from model  import *
from defs   import *

import functools
import logging

from django.conf import settings

USERFILE = "users.txt"
TAG_MAX  = 100

def update_tag_cloud_list():
    sumv = 0
    tags = Tag.gql('ORDER BY name ASC')
    e    = tags.fetch(TAG_MAX)

    local_tag_list = []

    for t in e:
        count = t.count
        if count>0:
            local_tag_list.append([str(t.key()),t.name,count])
            sumv = sumv + count

    #average posts
    tags_count=len(e)
    if tags_count > 0 and sumv> tags_count:
        avg = sumv / tags_count
    else:
        avg = 1

    #set font size
    for t in local_tag_list:
        font_size = 100*t[2]/avg
        if font_size >200:
            font_size = 200
        elif font_size < 90:
            font_size = 90

        t.append(font_size) #t[3]
    return local_tag_list



class MyRequestHandler(webapp.RequestHandler):
    """
    Base class for all request handlers in this application. This class
    serves primarily to isolate common logic.
    """

    def get_template(self, template_name):
        """
        Return the full path of the template.

        :Parameters:
            template_name : str
                Simple name of the template

        :rtype: str
        :return: the full path to the template. Does *not* ensure that the
                 template exists.
        """
        return os.path.join(os.path.dirname(__file__),
                            TEMPLATE_SUBDIR,
                            template_name)

    def render_template(self, template_name, template_vars):
        """
        Render a template and write the output to ``self.response.out``.

        :Parameters:
            template_name : str
                Simple name of the template

            template_vars : dict
                Dictionary of variables to make available to the template.
                Can be empty.
        """
        template_path = self.get_template(template_name)
        self.response.out.write(template.render(template_path, template_vars))


class NotFoundPageHandler(MyRequestHandler):
    def get(self):
        #self.error(404)
        self.render_template('404.djhtml',None)

def is_valid_user(user):
    emails = open(USERFILE).readlines()
    for e in emails:
        if e[0]=='#':
            continue
        if e[-1]=='\n' or e[-1]=='\r':
            e = e[0:-1]
        if user.email()==e:
            return True
    return False

class Index(MyRequestHandler):
    """
    the root page
    """
    def do_get(self,tag,bkmk,get_old,get_page):
        #get_my_tweets()
        #logging.info(get_my_twitter_profile())
        try:
            if tag is None:
                tagobj = None
            else:
                q = db.Query(Tag)
                q.filter('__key__ = ', db.Key(tag))
                tagobj = q.get()

            entries,next_bkmk,prev_bkmk = get_page(tagobj,bkmk)
        except datastore_errors.BadKeyError:
            self.render_template('404.djhtml',None)
            return

        user  = users.get_current_user()
        if user and not is_valid_user(user):
            user = None

        if user:
            user_url = users.create_logout_url(self.request.uri)
        else:
            user_url = users.create_login_url(self.request.uri)

        template_values = {
            'entries'        : entries,
            'user_url'       : user_url,
            'user'           : user,
            'tag'            : tag,
            'is_view'        : True,
            'tag_cloud_list' : update_tag_cloud_list()
        }

        if get_old:
            template_values['new_page_bkmk'] = prev_bkmk
            template_values['old_page_bkmk'] = next_bkmk
        else:
            template_values['new_page_bkmk'] = next_bkmk
            template_values['old_page_bkmk'] = prev_bkmk


        self.render_template('index.djhtml',template_values)

    def get(self,new_page_bookmark=None):
        self.do_get(None,new_page_bookmark,True,Entry.get_old_page)

class PrevPage(Index):
    def get(self,bookmark=None):
        self.do_get(None,bookmark,False,Entry.get_new_page)

class TagIndex(Index):
    def get(self,tag,bookmark=None):
        self.do_get(tag,bookmark,True,Entry.get_old_page)

class TagPrevPage(Index):
    def get(self,tag,bookmark=None):
        self.do_get(tag,bookmark,False,Entry.get_new_page)


def logged_in_as_owner(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = users.get_current_user()
        if user is None:
            if self.request.method == "GET":
                self.redirect(users.create_login_url(self.request.uri))
                return
            self.error(403)
        else:
            if  kwargs.has_key('key'):
                #check if the logged in user is the specified entry's owner
                try:
                    entry = Entry.get(key)
                except datastore_errors.BadKeyError:
                    self.error(403)
                if entry.owner.user_id()<>user.user_id():
                    self.error(403)
            return method(self, *args, **kwargs)
    return wrapper


class UpdateEntry(MyRequestHandler):
    """
    edit post page
    """
    @logged_in_as_owner
    def get(self,eid = None):
        if eid is None:
            entry  = None
            format = 'rs'
        else:
            entry  = Entry.get(eid)
            format = entry.format

        template_values = {
            'id'       : eid,
            'user'     : users.get_current_user(),
            'entry'    : entry,
            'format'   : format,
            'user_url' : users.create_logout_url(self.request.uri),
        }
        self.render_template('update_entry.djhtml',template_values)

class PostEntry(MyRequestHandler):
    """
    post entry
    """
    def get(self):
        self.redirect('/')

    @logged_in_as_owner
    def post(self,eid = None):
        def get_contents(entry,request):
            entry.title   = request.get('title')
            entry.subject = request.get('subject')
            entry.text    = request.get('text')
            entry.format  = request.get('texttype')

            private = request.get('private')
            entry.private = (private is not None) and len(private)>0

            tags = []

            for t in request.get('tags').split():
                q = Tag.gql('WHERE name = :1',t)
                tag = q.get()
                if tag is None:
                    tag = Tag(name=t)
                    tag.put()
                tags.append(tag)

            tag_keys = [ i.key() for i in tags ]

            #removed tags
            for t in entry.tags:
                if t not in tag_keys:
                    tag = Tag.get(t)
                    tag.count-=1
                    #logging.info("tag %s count-1 = %d"%(tag.name,tag.count))
                    tag.put()
                    entry.tags.remove(t)

            #new tags
            for t in tags:
                if t.key() not in entry.tags:
                    entry.tags.append(t.key())
                    t.count+=1
                    #logging.info("tag %s count+1 = %d"%(t.name,t.count))
                    t.put()

        if eid:
            #update
            try:
                entry = Entry.get(eid)
            except datastore_errors.BadKeyError:
                self.render_template('404.djhtml',None)
                return
        else:
            #new
            #find out current max entry id
            q = Entry.gql('ORDER BY entry_id DESC')
            e = q.fetch(1)
            if e is None:
                eid = 1
            else:
                eid = e[0].entry_id +1
            entry = Entry(entry_id=eid)

        get_contents(entry,self.request)
        entry.put()

        self.redirect('/')

class ShowEntry(MyRequestHandler):
    def get(self,eid=None):
        if eid is None:
            self.redirect("/")
        else:
            user  = users.get_current_user()
            if user:
                user_url = users.create_logout_url(self.request.uri)
            else:
                user_url = users.create_login_url(self.request.uri)

            try:
                entry = Entry.get(eid)
            except datastore_errors.BadKeyError:
                self.render_template('404.djhtml',None)
                return

            template_values = {
                'entry'     : entry,
                'user_url'  : user_url,
                'user'      : user,
                'highlight_keyword' : None,
                'is_view'    : True,
                'show_detail': True
                }
        self.render_template('detail.djhtml',template_values)
