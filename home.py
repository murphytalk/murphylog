import sys,logging

sys.path.insert(0, 'lib')
sys.path.insert(0, 'lib/docutils.zip')

from blog import *

template.register_template_library('template_tag_filter.tag_filter')

app = webapp.WSGIApplication(
    [(r'/'              , Index),
     (r'/prev/([0-9]+)/', PrevPage),
     (r'/next/([0-9]+)/', Index),
     (r'/new/'          , UpdateEntry),
     (r'/edit/([0-9]+)/', UpdateEntry),
     (r'/post/([0-9]+)/', PostEntry),
     (r'/post-new/'     , PostEntry),
     (r'/blog/([0-9]+)/', ShowEntry),
     (r'/archive/([0-9]+)/'                    , ArchivePage),
     (r'/tag/([0-9a-zA-Z\_]+)/'                , TagIndex),
     (r'/tag/([0-9a-zA-Z\_]+)/prev/([0-9a]+)/' , TagPrevPage),
     (r'/tag/([0-9a-zA-Z\_]+)/next/([0-9a]+)/' , TagIndex),
     (r'/feed.xml'              , AtomFeedHandler),
     (r'/.*'                    , NotFoundPageHandler)
    ],
    debug=True)
