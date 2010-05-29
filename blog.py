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
        self.response.out.write(template.render(template_path, template_vars))


class HomePage(MyRequestHandler):
    """
    the root page
    """
    def get(self):
        entries,bookmark = Entry.get_next_page(None)
        user             = users.get_current_user()
        if user:
            user_url = users.create_logout_url(self.request.uri)
        else:
            user_url = users.create_login_url(self.request.uri)
        template_values = {
            'entries'   : entries,
            'user_url'  : user_url,
            'user'      : user,
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
    def get(self,id):
        logging.info("UpdateEntry::get,id=%s"%id)
        template_values = {
            'id'       : id,
            'user'     : users.get_current_user(),
            'user_url' : users.create_logout_url(self.request.uri),
            'is_update': True,
        }
        self.render_template('update_entry.djhtml',template_values)

class NewEntry(UpdateEntry):
    """
    new post page
    @todo : no smarter way? like what django does: capture parameters from url?
    """
    def get(self):
        return super(NewEntry, self).get(None)

class PostEntry(MyRequestHandler):
    """
    post entry
    """
    @logged_in_as_owner
    def get(self):
        pass
