# -*- coding: utf-8 -*-
# coding=utf-8
import os.path

from google.appengine.ext        import webapp
from google.appengine.ext.webapp import template
from google.appengine.api        import users

from model  import *
from defs   import *

import functools
import logging

from django.conf import settings


#class NotFoundPageHandler(webapp.RequestHandler):
#    def get(self):
#        logging.info("it's a 404")
#        self.error(404)
#        #self.response.out.write('<Your 404 error html page>')

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


class Index(MyRequestHandler):
    """
    the root page
    """
    def do_get(self,bkmk,get_old,get_page):
        entries,next_bkmk,prev_bkmk = get_page(bkmk)
        user  = users.get_current_user()
        if user:
            user_url = users.create_logout_url(self.request.uri)
        else:
            user_url = users.create_login_url(self.request.uri)

        template_values = {
            'entries'       : entries,
            'user_url'      : user_url,
            'user'          : user,
            'is_view'       : True,
        }

        if get_old:
            template_values['new_page_bkmk'] = prev_bkmk
            template_values['old_page_bkmk'] = next_bkmk
        else:
            template_values['new_page_bkmk'] = next_bkmk
            template_values['old_page_bkmk'] = prev_bkmk

        self.render_template('index.djhtml',template_values)

    def get(self,new_page_bookmark=None):
        self.do_get(new_page_bookmark,True,Entry.get_old_page)

class PrevPage(Index):
    def get(self,bookmark=None):
        self.do_get(bookmark,False,Entry.get_new_page)

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
            if  kwargs.has_key('id'):
                #check if the logged in user is the specified entry's owner
                self.error(403)
            return method(self, *args, **kwargs)
    return wrapper


class UpdateEntry(MyRequestHandler):
    """
    edit post page
    """
    @logged_in_as_owner
    def get(self,key = None):
        logging.info("UpdateEntry,key=",key)
        if key is None:
            entry  = None
            format = 'rs'
        else:
            entry  = Entry.get(key)
            format = entry.format

        template_values = {
            'key'      : key,
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
    def post(self,key = None):
        def get_contents(entry,request):
            entry.title   = request.get('title')
            entry.subject = request.get('subject')
            entry.text    = request.get('text')
            entry.format  = request.get('texttype')

            #logging.info("private="+request.get('private'))
            private = request.get('private')
            entry.private = private is not None

        if key:
            #update
            entry = Entry.get(key)
        else:
            #new
            entry = Entry()

        get_contents(entry,self.request)
        entry.put()

        self.redirect('/')

class ShowEntry(MyRequestHandler):
    def get(self,key=None):
        if key is None:
            self.redirect("/")
        else:
            user  = users.get_current_user()
            if user:
                user_url = users.create_logout_url(self.request.uri)
            else:
                user_url = users.create_login_url(self.request.uri)
            entry = Entry.get(key)
            template_values = {
                'entry'     : entry,
                'user_url'  : user_url,
                'user'      : user,
                'highlight_keyword' : None,
                'is_view'    : True,
                'show_detail': True
                }
        self.render_template('detail.djhtml',template_values)
