from django.conf.urls.defaults import *

urlpatterns = patterns('',
     #index
     (r'^$','murphytalk_django.murphylog.views.index'),
     #specified page                       
     (r'^page/(?P<page>[0-9]+)/$','murphytalk_django.murphylog.views.index'),
     #post detail
     (r'^(?P<eid>[0-9]+)/$','murphytalk_django.murphylog.views.detail'),
     (r'^(?P<eid>[0-9]+)/(?P<highlightWord>.*)/$','murphytalk_django.murphylog.views.detail'),
     #specified tag
     (r'^tag/(?P<tag_id>[0-9]+)/$','murphytalk_django.murphylog.views.taggedIndex'),
     #specified tag page
     (r'^tag/(?P<tag_id>[0-9]+)/page/(?P<page>[0-9]+)/$','murphytalk_django.murphylog.views.taggedIndex'),
     #login
     (r'^login/$','murphytalk_django.murphylog.views.login'),
     #logout
     (r'^logout/$','murphytalk_django.murphylog.views.logout'),
     #update entry
     (r'^edit/(?P<eid>[0-9]+)/$','murphytalk_django.murphylog.views.update'),
     #detail (after post)
     (r'^entryposted/(?P<eid>[0-9]+)/$','murphytalk_django.murphylog.views.postedDetail'),
     #new post
     (r'^new/$','murphytalk_django.murphylog.views.new'),
     #post free comment
     (r'^postfreecomment/$', 'murphytalk_django.murphylog.views.post_free_comment'),
     #comment posted                       
     (r'^posted/$', 'murphytalk_django.murphylog.views.commentPosted'),
     #search
     (r'^search/(?P<searchFor>.*)/$', 'murphytalk_django.murphylog.views.search'),
)

