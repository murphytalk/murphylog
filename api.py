try:
    import dev_appserver
    dev_appserver.fix_sys_path()
except ImportError:
    print('Please make sure the App Engine SDK is in your PYTHONPATH.')
    raise

import codecs
from datetime import timedelta 
from model import *
from google.appengine.ext.remote_api import remote_api_stub

def download_entry(project_id,entry_id):
    def gen_filename(d):
        #print d
        return "%04d%02d%02d-%02d%02d.%s"%(d.year,d.month,d.day,d.hour,d.minute,'rst' if entry.format <> 'bb' else 'md')

    def gen_category(tags):
        if 'DayDream' in tags:
            return 'Misc'
        if 'ReadingNotes' in tags:
            return 'Book'
        if 'Fallout' in tags:
            return 'Game'
        if 'Game' in tags:
            return 'Game'
        if 'Memo' in tags:
            return 'Memo'
        return 'Computer'


    remote_api_stub.ConfigureRemoteApiForOAuth(
        '{}.appspot.com'.format(project_id),'/_ah/remote_api')
    entry = Entry.get(entry_id)
    if entry is None:
        print "None entry for id %s"%entry_id
    else:
        d = entry.last_edit + timedelta(hours=9)
        file = codecs.open(gen_filename(d),'w','utf-8')
        file.write('Title: %s\n'%entry.title)
        file.write('Category: %s\n'%gen_category(entry.tags))
        file.write('Tags: %s\n'%entry.get_tags_as_str(','))
        file.write('Date: %04d-%02d-%02d %02d:%02d\n'%(d.year,d.month,d.day,d.hour,d.minute))
        file.write('\n\n%s\n\n%s'%(entry.subject,entry.text))
        file.close()

if __name__ == '__main__':
    eid = 1
    download_entry('murphy-log',str(eid))
