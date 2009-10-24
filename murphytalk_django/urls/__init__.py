from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # ----------- django apps ----------------------------------
    #admin:
     (r'^admin/(.*)', admin.site.root),

    #comments
    #(r'^comments/', include('django.contrib.comments.urls')),

    # ----------- my apps ----------------------------------
    #blog:
     #map root url to blog
     (r'^$', include('murphytalk_django.urls.blog')),
     (r'^blog/', include('murphytalk_django.urls.blog')),

    # ----------- 3rd party apps ----------------------------------
    #filebrowser:
     (r'^admin/filebrowser/', include('murphytalk_django.filebrowser.urls')),
)

if settings.DEBUG:
    # ----------- media static files,for development only --------
    if settings.LINUX:
        urlpatterns += patterns('',
                                (r'^media/(.*)$', 'django.views.static.serve', {'document_root': '/home/murphy/work/django/HOMEPAGE/murphytalk_django/my_django_site/media'}),
                                (r'^blogimages/(.*)$', 'django.views.static.serve', {'document_root': '/home/media/BACKUP_DATA/HOMEPAGE/blogimages'}),
                               )
    else:
        urlpatterns += patterns('',
                                (r'^media/(.*)$', 'django.views.static.serve', {'document_root': 'C:/LM/Projects/extra/Django/murphytalk_django/my_django_site/media'}),
                               )
