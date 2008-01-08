#this script is supposed to be run from django shell
from load_frog import Loader
from murphytalk_django.murphylog.models import Entry
from murphytalk_django.tags.models import Tag
from django.contrib.auth.models import User
from datetime import datetime

OLD_IMG_PATH = "/frog/files/murphytalk/"
NEW_IMG_PATH = "/media/blog/img/BLOG/"

#map id in frog to id in django
cmap={3:0,4:1,5:2,6:3,8:4,9:5,10:6,11:7,12:8,14:9}

blogdata="/home/BACKUP/FrogBlog/blogdata"
username="murphytalk"
loader=Loader(blogdata,username)
all=loader.list_all()
all.reverse()


u=User.objects.get(id=1)

eid = 1
for datestr,id in all:
    frog_entry  =loader.load_entry(datestr,id)

    #frog data entry might not have texttype attrib,which means text type is bbcode
    if not hasattr(frog_entry,'texttype'):
        txt='bbcode'
    else:
        txt=frog_entry.texttype

    #datetime
    print frog_entry.datetime
    dt=datetime(int(frog_entry.datetime[0][:4]),int(frog_entry.datetime[0][5:7]),int(frog_entry.datetime[0][8:]),int(frog_entry.datetime[1][:2]),int(frog_entry.datetime[1][3:]))
    print dt
    last=datetime.fromtimestamp(frog_entry.lastedited)
    if last.year<2000:
        last=dt

    #updat img path
    if frog_entry.text.find(OLD_IMG_PATH)>=0:
        frog_entry.text=frog_entry.text.replace(OLD_IMG_PATH,NEW_IMG_PATH)

    if frog_entry.text2 and frog_entry.text2.find(OLD_IMG_PATH)>=0:
        frog_entry.text2=frog_entry.text2.replace(OLD_IMG_PATH,NEW_IMG_PATH)
        
    print 'processing entry posted in',frog_entry.datetime,'text code is',txt

    tagid=cmap[frog_entry.category]+1
    print 'category from frog is %d,mapping to %d'%(frog_entry.category,tagid)
    tag=Tag.objects.get(id=tagid)
    #save obj
    django_entry=Entry(owner=u,title=frog_entry.title,post_date=dt,subject=frog_entry.text,text=frog_entry.text2,text_type=txt[:2],last_edit=last,private=False)
    django_entry.id=eid
    #related objs
    django_entry.tags.add(tag)
    print "post date before save",django_entry.post_date
    django_entry.save()
    print "entry with id=%d saved"%eid
    print "post date after save",django_entry.post_date
    eid=eid+1



