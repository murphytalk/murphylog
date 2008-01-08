from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    # ----------- django apps ----------------------------------                        
    #admin:
     (r'^admin/', include('django.contrib.admin.urls')),
                       
    #comments
    #(r'^comments/', include('django.contrib.comments.urls.comments')),

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
                                (r'^media/(.*)$', 'django.views.static.serve', {'document_root': '/home/murphy/BACKUP_DATA/work/django/HOMEPAGE/murphytalk_django/my_django_site/media'}),
                                (r'^blogimages/(.*)$', 'django.views.static.serve', {'document_root': '/home/murphy/BACKUP_DATA/HOMEPAGE/blogimages'}),                       
                               )
    else:
        urlpatterns += patterns('',
                                (r'^media/(.*)$', 'django.views.static.serve', {'document_root': 'C:/LM/Projects/extra/Django/murphytalk_django/my_django_site/media'}),
                               )
