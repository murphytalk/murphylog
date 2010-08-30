#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from google.appengine.ext             import webapp
from google.appengine.ext.webapp      import template
from google.appengine.ext.webapp.util import run_wsgi_app

import sys,logging
sys.path.insert(0, 'lib')
sys.path.insert(0, 'lib/docutils.zip')

from blog import *

template.register_template_library('template_tag_filter.tag_filter')

application = webapp.WSGIApplication(
  [(r'/'              , Index),
   (r'/prev/([0-9]+)/', PrevPage),
   (r'/next/([0-9]+)/', Index),
   (r'/new/'          , UpdateEntry),
   (r'/edit/([0-9]+)/', UpdateEntry),
   (r'/post/([0-9]+)/', PostEntry),
   (r'/post-new/'     , PostEntry),
   (r'/blog/([0-9]+)/', ShowEntry),
   (r'/tag/([0-9a-zA-Z\_]+)/'                , TagIndex),
   (r'/tag/([0-9a-zA-Z\_]+)/prev/([0-9a]+)/' , TagPrevPage),
   (r'/tag/([0-9a-zA-Z\_]+)/next/([0-9a]+)/' , TagIndex),
   (r'/.*'                    , NotFoundPageHandler)
  ],
  debug=True)


def main():
  logging.getLogger().setLevel(logging.DEBUG)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
