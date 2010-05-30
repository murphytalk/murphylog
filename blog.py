# -*- coding: utf-8 -*-
import os.path

from google.appengine.ext        import webapp
from google.appengine.ext.webapp import template
from google.appengine.api        import users

from model  import *
from defs   import *

import functools
import logging

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
        logging.info("load template:%s"%template_path)
        self.response.out.write(template.render(template_path, template_vars))


class HomePage(MyRequestHandler):
    """
    the root page
    """
    def get(self):
        entries,bookmark = Entry.get_next_page(None)
        logging.info("num of entries = %d,bookmark=%s"%(len(entries),bookmark))
        user             = users.get_current_user()
        if user:
            user_url = users.create_logout_url(self.request.uri)
        else:
            user_url = users.create_login_url(self.request.uri)
        template_values = {
            'entries'   : entries,
            'user_url'  : user_url,
            'user'      : user,
            'highlight_keyword' : None,
            'is_view'   : True,
        }

        self.render_template('index.djhtml',template_values)


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
            logging.info("args num=%d"%len(args))
            for k in kwargs:
                logging.info("kwargs:%s"%k)
            logging.info("---------------")
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
        logging.info("UpdateEntry::get,key=%s"%key)
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
            logging.info("title=%s"%entry.title)
            entry.subject = request.get('subject')
            entry.text    = request.get('text')
            private       = False #request.get('is_private')
            entry.private = private and len(private)>0
            entry.format  = request.get('texttype')

        logging.info("post,key=%s"%key)
        if key:
            #update
            entry = Entry.get(key)
        else:
            #new
            entry = Entry()

        logging.info("TITLE = <%s>"%self.request.get('title'))
        get_contents(entry,self.request)
        entry.put()

        self.redirect('/')
