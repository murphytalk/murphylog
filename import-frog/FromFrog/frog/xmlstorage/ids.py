#
#   XML-FILES-BASED STORAGE OBJECT IMPLEMENTATION: ID GENERATOR
#
#   This implements an unique-ID-generator that writes its 'state' in
#   an XML file in the filesystem.
#

from xml.dom import minidom
import xml.dom
import threading
import os
from transactionalfile import TransactionalFile
from frog import FILEPROT

import logging
log=logging.getLogger("Snakelets.logger")


FILENAME = "ids.xml"
IDNAMES = ["blogentry", "comment", "category"] 


class IDGenerator:
    def __init__(self, path):
        self.idfilename = os.path.join(path, FILENAME)
        self.lock=threading.Lock()
        self.ids={}
        self.load(IDNAMES)
        
    def create(self, idnames):
        self.ids={}
        for name in idnames:
            self.ids[name]=0
        self.store()

    def load(self, idnames=None):
        self.ids=dict.fromkeys(IDNAMES,0)
        try:
            dom=minidom.parse(self.idfilename)
            for child in dom.documentElement.childNodes:
                if child.nodeType==xml.dom.Node.ELEMENT_NODE:
                    self.ids[str(child.nodeName)] = int(child.firstChild.nodeValue)
        except EnvironmentError,x:
            if idnames:
                self.create( idnames )
            else:
                raise

    def store(self):
        xml='<?xml version="1.0"?>\n<ids>\n'
        for (name,value) in self.ids.items():
            xml+=' <%s>%d</%s>\n' % (name,value,name)
        xml+='</ids>\n'
        newfile=TransactionalFile(self.idfilename,"wb")
        newfile.write(xml)
        newfile.commit()
        os.chmod(newfile.name, FILEPROT)

    def getId(self, idname):
        self.lock.acquire()   # could also have used file locking on the id storage file.
        try:
            self.ids[idname]+=1
            self.store()
            Id=self.ids[idname]
            log.debug("new id for %s: %d" % (idname, Id))
            return Id
        finally:
            self.lock.release()

if __name__=="__main__":
    import tempfile
    gen=IDGenerator(tempfile.gettempdir())
    print "IDFILE=",gen.idfilename
    
    print gen.getId("comment")
    print gen.getId("blogentry")
    print gen.getId("blogentry")
    print gen.getId("category")
    print gen.getId("foobar")

