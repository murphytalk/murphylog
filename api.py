try:
    import dev_appserver
    dev_appserver.fix_sys_path()
except ImportError:
    print('Please make sure the App Engine SDK is in your PYTHONPATH.')
    raise

import codecs
import sys, os
from datetime import timedelta 
from model import *
from google.appengine.ext.remote_api import remote_api_stub

def download_entry(project_id,entry_id):
    def is_rst(entry):
        return entry.format <> 'bb'

    def gen_filename(eid,d,rst,private):
        name = "%04d%02d%02d-%02d%02d-%s.%s"%(d.year,d.month,d.day,d.hour,d.minute,eid,'rst' if rst else 'md')
        return ("private-%s" % name) if private else name
    
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

    def write_title(f,rst,t):
        if rst:
            tline = '#'*(2*len(t))
            f.write('%s\n'%tline)
            f.write('%s\n'%t)
            f.write('%s\n'%tline)
        else:
            f.write('Title: %s\n'%t)

    def write_tags(f,rst,t):
        f.write( (':tags: %s\n' if rst else 'Tags: %s\n') % t)

    def write_category(f,rst,c):
        f.write((':category: %s\n' if rst else 'Category: %s\n') % c)

    def write_date(f,rst,y,M,d,h,m):
        f.write((':date: %04d-%02d-%02d %02d:%02d\n\n' if rst else 'Date: %04d-%02d-%02d %02d:%02d\n\n') %(y,M,d,h,m))

    remote_api_stub.ConfigureRemoteApiForOAuth(
        '{}.appspot.com'.format(project_id),'/_ah/remote_api')

    entry = Entry.get(entry_id)
    if entry is None:
        print "None entry for id %s"%entry_id
    else:
        d = entry.post_time + timedelta(hours=9)
        rst = is_rst(entry)
        file = codecs.open(gen_filename(entry_id,d,rst,entry.private),'w','utf-8')

        write_title(file,rst,entry.title)
        write_category(file,rst,gen_category(entry.get_tags_as_str(None)))
        write_tags(file,rst,entry.get_tags_as_str(','))
        write_date(file,rst,d.year,d.month,d.day,d.hour,d.minute)
        file.write('\n\n%s\n\n%s'%(entry.subject,'' if entry.text is None else entry.text))
        file.close()

if __name__ == '__main__':
    if len(sys.argv)!=3:
        print "need 2 arguments: start entry id , end entry id"
    else:
        id1 = int(sys.argv[1])
        id2 = int(sys.argv[2])
        for eid in range(id1,id2+1):
            print "downloading entry #%d ..."%eid
            download_entry('murphy-log',str(eid))
