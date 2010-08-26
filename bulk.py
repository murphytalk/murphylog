from google.appengine.ext   import db
from google.appengine.tools import bulkloader
from google.appengine.api   import users
import datetime
import model
"""
steps to import:

0)
cmd =
PYTHONPATH=. python2.5 `which appcfg.py` --config_file=bulk.py -A murphytalk-log --url=http://localhost:8080/remote_api

1) import tags csv (format : name, count) to GAE

cmd upload_data --kind=Tag --filename=in-tags.csv

2) export tags back to csv(format : key,name,count)

cmd download_data --kind=Tag --filename=out-tags.csv

now you know the key name for each tag in GAE

3) use the tag key to prepare a upload file for Entry,format:
 title,subject,text,owner(email),private,format,post_time(YYYY-MM-DD hh:ss:mm),last_edit,tagkey1;tagkey2

4) import the entry csv to GAE:

cmd upload_data --kind=Entry --filename=entry.csv

"""

def export_list(tag_lst):
    tags_key=''
    for t in tag_lst:
        tags_key += str(t)+';' # t is a Key obj
    tags_key = tags_key[:-1]
    return tags_key


class EntryExporter(bulkloader.Exporter):
    def __init__(self):
        bulkloader.Exporter.__init__(self,'Entry',
                                     [('title'    ,lambda x: x.encode('utf-8'),None),
                                      ('subject'  ,lambda x: x.encode('utf-8'),None),
                                      ('text'     ,lambda x: x.encode('utf-8'),None),
                                      ('owner'    ,lambda x: x.email()        ,None),
                                      ('private'  ,str,None),
                                      ('format'   ,str,None),
                                      ('post_time',lambda x: x.strftime('%Y-%m-%d %H:%M:%S'),None),
                                      ('last_edit',lambda x: x.strftime('%Y-%m-%d %H:%M:%S'),None),
                                      ('tags'     ,export_list,None)])


class TagExporter(bulkloader.Exporter):
    def __init__(self):
        bulkloader.Exporter.__init__(self,'Tag',
                                     [('__key__'  ,str,None),
                                      ('name'     ,str,None),
                                      ('count'    ,str,None)])


exporters = [EntryExporter,TagExporter]

def import_boolean(bstr):
    if bstr == 'True':
        return True
    else:
        return False

def import_list(tag_keyname):
    lst = []
    tag_keyname_lst = tag_keyname.split(';')
    for t in tag_keyname_lst:
        lst.append(db.Key(t))
    return lst

class EntryImporter(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self,'Entry' ,
                                   [('title'    ,lambda x: x.decode('utf-8')),
                                    ('subject'  ,lambda x: x.decode('utf-8')),
                                    ('text'     ,lambda x: x.decode('utf-8')),
                                    ('owner'    ,lambda x: users.User(x)),
                                    ('private'  ,import_boolean),
                                    ('format'   ,str),
                                    ('post_time',lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')),
                                    ('last_edit',lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')),
                                    ('tags'     ,import_list)])

class TagImporter(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self,'Tag',
                                   [('name' ,str),
                                    ('count',int)])

loaders = [EntryImporter,TagImporter]
