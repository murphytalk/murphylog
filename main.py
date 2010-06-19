#!/usr/bin/env python
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

import sys
sys.path.insert(0, 'lib')
sys.path.insert(0, 'lib/docutils.zip')

from blog import *

template.register_template_library('template_tag_filter.tag_filter')

application = webapp.WSGIApplication(
  [('/'                      , HomePage),
   ('/new/'                  , UpdateEntry),
   ('/edit/([0-9]*)/'        , UpdateEntry),
   ('/post/([0-9a-zA-Z\-]+)/', PostEntry),
   ('/post-new/'             , PostEntry),
   ('/blog/([0-9a-zA-Z\-]+)/', ShowEntry),
 #   ('/*'              , NotFoundPageHandler)
  ],
  debug=True)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
