#
#   XML-FILES-BASED STORAGE OBJECT IMPLEMENTATION
#
#   This implements data storage and retrieval services that write the data
#   in XML files in the filesystem. The storage engine's queries are 
#   implemented by scanning the files and directories in the specified
#   storage location on disk, and parsing the XML files into objects.
#   Storing objects on disk means converting the attributes to a XML document.
#   
#   The Storage Engine provides generic query functions,
#   the actual loading and storing of the objects (parsing/generating XML)
#   is implemented per storage object. The storage objects are to be used
#   as a base class for the 'real' object.
#

import os, time, copy, weakref
import sets, sre, pickle
import xml.dom
from xml.sax.saxutils import XMLGenerator
import frog.util
import frog.objects
from frog import FILEPROT, DIRPROT, STORAGE_FORMAT
from frog.storageerrors import StorageError
from transactionalfile import TransactionalFile

import logging
log=logging.getLogger("Snakelets.logger")

from ids import IDGenerator


def getXMLvalue(obj, attr):
    # returns the value of the given attribute of the object
    # as a unicode string object that can be written to an XML doc.
    v=getattr(obj,attr)
    if type(v) in (str, unicode):
 #       return unicode(v or u'')
 # LM -> our text already in utf8
        return v
    elif v is None:
        return u''
    else:
        return unicode(v)


def assertCompatibleVersion(version):
    if version!=STORAGE_FORMAT:
        raise StorageError("incompatible Frog storage format version: "+str(version)+" (expected: "+STORAGE_FORMAT+")")

#
#   This storage engine class must be instantiated on a per-user basis.
#   This means that every user has his own storage engine object.
#   All operations on this storage engine are defined for that user.
#
#   If you DON'T provide a specific user id, the engine is initialized
#   for 'global' usage, and only a few queries actually work
#   (the ones not defined for a specific user).
#
class XMLStorageEngine:

    def __init__(self, webapp, userid=None):
        if webapp:
            if type(webapp) in weakref.ProxyTypes:
                self.webapp = webapp                
            else:
                self.webapp = weakref.proxy(webapp)
            self.userid=userid
            self.storagebase=webapp.getConfigItem("storage")
            
            self.webapp.getContext().lockedBlogs=sets.Set()
        else:  # for test purposes
            self.storagebase, self.userid = userid

        if self.userid:
            self.storagepath=self.makeStoragePath()
            if not os.path.isdir(self.storagepath):
                raise StorageError("storage path does not exist: "+self.storagepath)
            self.idGenerator = IDGenerator(self.storagepath)
            
    def makeStoragePath(self, userid=None):
        return os.path.join(self.storagebase, userid or self.userid)

    def createNew(self, userid=None):
        return XMLStorageEngine(self.webapp, userid)

    def close(self):
        pass  # in case resources have to be freed

    def lockComments(self,blogId):
        log.debug("locking comments for blog %d..." % blogId)
        lockedBlogs=self.webapp.getContext().lockedBlogs
        tries=0
        while blogId in lockedBlogs:
            if tries>10:
                msg="blog entry %d is still locked after wait period" % blogId
                log.warn(msg)
                raise StorageError(msg)
            time.sleep(1)
            tries+=1
        lockedBlogs.add(blogId)
        log.debug("locked comments for blog %d" % blogId)
    def unlockComments(self,blogId):
        try:
            self.webapp.getContext().lockedBlogs.remove(blogId)
        except KeyError:
            pass
        log.debug("unlocked comments for blog %d" % blogId)

    def listUsers(self, useCache=True):
        # NOT-USER-SPECIFIC: return a list of all registered users
        # (optionally use cached userlist that is updated on a certain schedule)
        if useCache:
            return self.webapp.getContext().registeredusers
        else:
            storagepath = self.webapp.getConfigItem("storage")
            allusers = [entry for entry in os.listdir(storagepath) if os.path.isdir(os.path.join(storagepath, entry)) and entry.lower() != "cvs"]
            allusers = sets.Set(allusers)
            self.webapp.getContext().registeredusers = allusers   # update the cache
            # we also update the list of users that are real blogger users
            # XXX this is slow! it loads every user to check the accounttype...
            bloggers=sets.Set()
            for user in allusers:
                try:
                    u = self.loadUser(user)
                except StorageError,x:
                    log.warn("could not load user '%s': %s", user, str(x))
                else:
                    if u.accounttype==frog.ACCOUNTTYPE_BLOGGER:
                        bloggers.add(user)
            self.webapp.getContext().registeredbloggerusers = bloggers    # update the cache
            
            return allusers

    def listBloggerUsers(self):
        # return a list of all users that are real blog users (not login-only users)
        return self.webapp.getContext().registeredbloggerusers
        

    def isRegisteredUser(self, userid, useCache=True):
        # check if a given userid is from a registered user.
        return userid in self.listUsers(useCache)
        
    def loadUser(self, userid):
        # NOT-USER-SPECIFIC: load a User with the given userid
        if not userid:
            raise ValueError("userid may not be empty")
        if self.userid and self.userid==userid:
            # This storageEngine is alreay used for the requested user, reuse it!
            # (otherwise data corruption may occur)
            engine=self
        else:
            engine=XMLStorageEngine(self.webapp, userid)
        #storagepath = self.webapp.getConfigItem("storage")
        from frog.objects import User
        return User.load(engine, userid) # what about the user.directory ??? XXX


    def getUniqueId(self, category):
        return self.idGenerator.getId(category)

    def createBlogDirs(self,datestr):
        curdir=os.path.join(self.storagepath,datestr)
        if not os.path.isdir(curdir):
            os.mkdir(curdir)
            os.chmod(curdir, DIRPROT)
            path=os.path.join(curdir, "blogs")
            os.mkdir(path)
            os.chmod(path, DIRPROT)
            path=os.path.join(curdir, "comments")
            os.mkdir(path)
            os.chmod(path, DIRPROT)
        
    def createBlogDirsForToday(self):
        date = frog.util.isodatestr()
        curdir=os.path.join(self.storagepath,date)
        log.debug("creating blog dirs in "+curdir)
        if not os.path.isdir(curdir):
            os.mkdir(curdir)
            os.chmod(curdir, DIRPROT)
            path=os.path.join(curdir, "blogs")
            os.mkdir(path)
            os.chmod(path, DIRPROT)
            path=os.path.join(curdir, "comments")
            os.mkdir(path)
            os.chmod(path, DIRPROT)

    def listBlogEntryDates(self):
        # this data is updated on a certain schedule, and taken from the cache. Sorted from recent to old.
        return self.webapp.getContext().blogentrydates[self.userid][:]
        
    def countAllBlogEntries(self):
        # this data is updated on a certain schedule, and taken from the cache
        return self.webapp.getContext().articlecounts[self.userid]   # returns an int

    def listArticlesInMonth(self,year,month):
        # this data is updated on a certain schedule, and taken from the cache
        try:
            return self.webapp.getContext().articlesinmonth[self.userid][year,month]
        except KeyError:
            # data is not in the cache, read it from the storage
            # this is needed to be able to serve pages fast, even if the scheduled action didn't run
            self.webapp.getSnakelet("articlestats.sn").updateArticlesInMonth(self.userid, year, month)
            return self.webapp.getContext().articlesinmonth[self.userid][year,month]

    def listAllBlogEntries(self):
        # return a list of (date, blogid)
        # XXX because of dir walking this may become slow for many blog entries (altough it's for a single user only).
        all=[]
        def walker(arg, dirname, names):
            if "blogs" in names and os.path.isdir(os.path.join(dirname,"blogs")):
                names[:]=["blogs"]
                return
            if dirname.endswith(os.path.sep+"blogs"):
                date=dirname.split(os.path.sep)[-2]
                for n in names:
                    if n.endswith(".xml"):
                        all.append( (date, int(n.split('.')[0]) ) )
        os.path.walk(self.storagepath,walker,all)
        all.sort()
        all.reverse()
        return all
    
        
    def listBlogEntries(self, date):
        path=os.path.join(self.storagepath, date, "blogs")
        if os.path.isdir(path):
            entries = [ int(e[:-4]) for e in os.listdir(path) if e.endswith(".xml")]
            entries.sort()
            return entries      # ascending order (old-to-new)
        else:
            return []
        
    def getNumberOfComments(self, date, Id):
        # count the number of comments for a given blog entry.
        # XXX this implementation is slow; it scans the comments XML file
        #     to extract the commentlist count...
        filename = Comments.determineFileName(self.storagepath, date, Id)
        if os.path.isfile(filename):
            regex=sre.compile(r'<commentlist\s+count="([0-9]+)"')
            for line in open(filename):
                match=regex.search(line)
                if match:
                    return int(match.group(1))
            raise StorageError("cannot determine comment count")
        else:
            return 0

    def getEntryCategory(self, date, Id):
        # get the category for the given blog entry.
        # XXX this implementation is slow; it scans the comments XML file
        filename = BlogEntry.determineFileName(self.storagepath, date, Id)
        regex=sre.compile('<category>(.+)</category>')
        for line in open(filename):
            match=regex.search(line)
            if match:
                return int(match.group(1))
        raise StorageError("cannot determine category")


    def listActiveArticles(self):
        # Return a list ( mtime, numcomments, articledatetime, articleid) of the most recently
        # modified articles (sorted; most recent first, older near the end).
        # this data is updated on a certain schedule, and taken from the cache
        return self.webapp.getContext().activearticles[self.userid][:]

    def listPopularArticles(self):
        # Return 2 lists:
        # 1st: list of most views (numviews, articledatetime, articleid)
        # 1st: list of most comments (numcomments, articledatetime, articleid)
        # lists are sorted (most views/comments are first).
        # this data is updated on a certain schedule, and taken from the cache
        try:
            counts = self.webapp.getContext().articlereads[self.userid].items()
        except KeyError:
            # not yet in cache, read the stored file or create it if it doesn't exist
            counts = self._loadArticleReads(self.storagepath).items()

        counts = [ (v,k) for (k,v) in counts ]
        counts.sort()
        counts=counts[-10:]
        counts.reverse()
        popular_views=[]
        for (numreads, article) in counts:
            (date,time), articleid=eval(article)
            numcomments=self.getNumberOfComments(date, articleid) # XXX slow... ( not cached )
            popular_views.append( (numreads, numcomments, date, articleid) )
        popular_comments=[]
        return popular_views, popular_comments

    def countReads(self, entry, increase=True, request=None):
        # increase the article read count by 1 and return the new value.
        # this uses the cache, which is stored on disk on a certain schedule.
        # the read counts are stored in a shelve file ( key=article key str, value=readcount int)
        key = repr( (entry.datetime, entry.id) )
        try:
            counts = self.webapp.getContext().articlereads[self.userid]
        except KeyError:
            # not yet in cache, read the stored file or create it if it doesn't exist
            counts = self._loadArticleReads(entry.getStoragePath())
        if increase:
            count=counts[key]=counts.get(key,0)+1
            ua="???"
            if request:
                ua=request.getUserAgent()
            msg="READCOUNT++ article=%d %r '%s'; useragent=%s" % (entry.id, entry.datetime, entry.title,ua)
            log.debug(msg)   # log the readcount message so you can check who or what is reading the stuff
        else:
            count=counts[key]=counts.get(key,0)
        return count

    def _loadArticleReads(self, storagepath):
        filename = os.path.join(storagepath, "articlereads.pickle")
        try:
            counts = pickle.load(open(filename,"rb"))
        except IOError:
            counts = {}
            pickle.dump(counts, open(filename,"wb"))
        self.webapp.getContext().articlereads[self.userid] = counts
        return counts
        

# --------------------------- STORAGE OBJECT BASE CLASSES ------------------


#
#   abstract base class for XML-persistence classes
#   
class _XMLObject(object):
    def __init__(self, storageengine):
        self._engine=storageengine
        self.id=None
    def makeId(self, category):
        if self.id is None:
            self.id = self._engine.getUniqueId(category)
        return self.id
    def getStoragePath(self):
        return self._engine.storagepath
    def remove(self):
        log.debug("remove %s: %s" % (str(self.id), self.__class__.__name__))
        del self._engine
        del self.id


    # storage object should implement the following methods:
    #
    #  load(storageEngine, id)  [classmethod]  - load from storage, returns new object instance
    #  store()   - write current object to storage
    #  remove()  - remove current object from storage
    
 
#
#   USER    xml-storage object
#

class User(_XMLObject):

    def store(self):
        self.id=self.userid
        self.version=STORAGE_FORMAT

        log.debug("storing User "+self.id)
        try:
            outf=TransactionalFile(User.determineFileName(self.getStoragePath()))
            gen=XMLGenerator(out=outf, encoding="UTF-8")
            gen.startDocument()
            gen.startElement("user",{}); gen.characters("\n")
            for attr in self.__slots__+['userid','name','password']:
                if attr=="password":
                    gen.startElement("passwordhash",{});
                    gen.characters(self.password.encode("hex"));
                    gen.endElement("passwordhash"); gen.characters("\n")
                elif attr=="links":
                    gen.startElement("links",{}); gen.characters("\n")
                    for (name, url) in self.links.items():
                        gen.startElement("link", {"name":name, "url":url}); gen.endElement("link"); gen.characters("\n")
                    gen.endElement("links"); gen.characters("\n")
                elif attr=="displaystrings":
                    gen.startElement("displaystrings",{}); gen.characters("\n")
                    for (name, string) in self.displaystrings.items():
                        gen.startElement("string", {"name":name, "value":(string or u"")}); gen.endElement("string"); gen.characters("\n")
                    gen.endElement("displaystrings"); gen.characters("\n")
                elif attr=="categories":
                    gen.startElement("categories",{}); gen.characters("\n")
                    for cat in self.categories.values():
                        cat.store()
                        cat.putInXML(gen)
                    gen.endElement("categories"); gen.characters("\n")
                else:
                    # other attribute
                    gen.startElement(attr,{});
                    gen.characters(getXMLvalue(self, attr));
                    gen.endElement(attr); gen.characters('\n')
                
            gen.endElement("user")
            gen.endDocument()
            outf.commit()
            os.chmod(outf.name, FILEPROT)
        except EnvironmentError,x:
            raise StorageError(str(x))

    def load(clazz, storageengine, Id):
        if storageengine.userid != Id:
            raise StorageError("using other user's storage engine to load a different user")
        log.debug("loading User "+Id)
        try:
            dom=xml.dom.minidom.parse(clazz.determineFileName(storageengine.storagepath))
            return clazz._loadXML(storageengine, dom.documentElement)
        except EnvironmentError,x:
            raise StorageError(str(x))
    load=classmethod(load)
    
    def _loadXML(clazz, storageengine, rootnode):
        userid = rootnode.getElementsByTagName("userid")[0].firstChild.nodeValue
        accounttype = rootnode.getElementsByTagName("accounttype")[0].firstChild.nodeValue
        pwdhash = rootnode.getElementsByTagName("passwordhash")[0].firstChild.nodeValue
        pwdhash=str(pwdhash).decode("hex")
        # the object constructor:
        #directory = os.path.join(storageengine.webapp.getConfigItem("files"), userid)   # the user's files directory
        directory = None
        obj=clazz(storageengine, userid, None, accounttype, passwordhash=pwdhash, directory=directory)
        
        for child in rootnode.childNodes:
            if child.nodeType==xml.dom.Node.ELEMENT_NODE:
                if child.nodeName=="version":
                    assertCompatibleVersion(child.firstChild.nodeValue)
                    obj.version=child.firstChild.nodeValue
                elif child.nodeName=="colorstyle":
                    obj.colorstyle=int(child.firstChild.nodeValue)
                elif child.nodeName=="smileycolor":
                    obj.smileycolor=int(child.firstChild.nodeValue)
                elif child.nodeName=="searchenabled":
                    obj.searchenabled = child.firstChild.nodeValue.lower() == "true"
                elif child.nodeName=="showlogin":
                    obj.showlogin = child.firstChild.nodeValue.lower() == "true"
                elif child.nodeName=="onlyregisteredcommenting":
                    obj.onlyregisteredcommenting = child.firstChild.nodeValue.lower() == "true"
                elif child.nodeName=="usepuzzles":
                    obj.usepuzzles = child.firstChild.nodeValue.lower() == "true"
                elif child.nodeName=="mailnotify":
                    obj.mailnotify = child.firstChild.nodeValue.lower() == "true"
                elif child.nodeName=="countreads":
                    obj.countreads = child.firstChild.nodeValue.lower() == "true"
                elif child.nodeName=="rssenabled":
                    obj.rssenabled = child.firstChild.nodeValue.lower() == "true"
                elif child.nodeName=="commentsmileys":
                    obj.commentsmileys = child.firstChild.nodeValue.lower() == "true"
                elif child.nodeName=="smileys":
                    obj.smileys = child.firstChild.nodeValue.lower() == "true"
                elif child.nodeName=="customfrontpage":
                    obj.customfrontpage = child.firstChild.nodeValue.lower() == "true"
                elif child.nodeName=="links":
                    obj.links={}
                    for child in child.childNodes:
                        if child.nodeType==xml.dom.Node.ELEMENT_NODE and child.nodeName=="link":
                            d=dict(child.attributes.items())
                            obj.links[d["name"]]=d["url"]
                elif child.nodeName=="displaystrings":
                    obj.displaystrings={}
                    for child in child.childNodes:
                        if child.nodeType==xml.dom.Node.ELEMENT_NODE and child.nodeName=="string":
                            d=dict(child.attributes.items() )
                            obj.displaystrings[d["name"]]=d["value"]
                elif child.nodeName=="categories":
                    obj.categories={}
                    for child in child.childNodes:
                        if child.nodeType==xml.dom.Node.ELEMENT_NODE and child.nodeName=="category":
                            cat=frog.objects.Category._loadXML(storageengine, child)
                            obj.categories[cat.id]=cat
                elif child.nodeName not in ("userid", "passwordhash"):
                    # other attribute.
                    if child.firstChild:
                        setattr(obj, child.nodeName, child.firstChild.nodeValue)
                    else:
                        setattr(obj, child.nodeName, None)

        assertCompatibleVersion(obj.version)
        return obj
    _loadXML=classmethod(_loadXML)
    
    def determineFileName(storagepath):
        return os.path.join(storagepath, "user.xml")
    determineFileName=staticmethod(determineFileName)

    def storage_determineCategoryCounts(self):
        # scan all blog entries and count the categories. Return a dict of catId -> Category object.
        log.debug("update category counts for user "+self.userid)
        allentries = self._engine.listAllBlogEntries()
        catcounts={}
        for date, Id in allentries:
            cat=self._engine.getEntryCategory(date,Id)
            catcounts.setdefault(cat,0)
            catcounts[cat]+=1
        cats={}
        for cId, count in catcounts.items():
            name=self.categories[cId].name
            category = frog.objects.Category(self._engine, name, count)
            category.id=cId
            cats[cId]=category
        return cats



#
#   CATEGORY     xml-storage-object
#
class Category(_XMLObject):

    def store(self):
        self.makeId("category")
        # categories are not loaded & stored by themselves, they are collected in a list in User objects.

    def putInXML(self, xmlgen):
        xmlgen.startElement("category",{"id":str(self.id), "name":self.name, "count": str(self.count)})
        xmlgen.endElement("category")
        xmlgen.characters("\n")
        
    def _loadXML(clazz, storageengine, rootnode):
        obj=object.__new__(clazz)
        obj._engine=storageengine
        if rootnode.attributes:
            obj.id=int(rootnode.attributes["id"].nodeValue)
            obj.count=int(rootnode.attributes["count"].nodeValue)
            obj.name=rootnode.attributes["name"].nodeValue
        return obj
    _loadXML=classmethod(_loadXML)

        
        
#
#   BLOGENTRY    xml-storage object
#
class BlogEntry(_XMLObject):
    
    def store(self):
        self.makeId("blogentry")
        log.debug("storing BlogEntry %s/%d" % (self.datetime[0],self.id))
        try:
            outf=TransactionalFile(BlogEntry.determineFileName(self.getStoragePath(), self.datetime[0], self.id) , "wb")
            gen=XMLGenerator(out=outf, encoding="UTF-8")
            gen.startDocument()
            gen.startElement("blogentry",{"id":str(self.id)}); gen.characters("\n")
            for attr in self.__slots__:
                if attr=="datetime":
                    gen.startElement("timestamp",{"date":self.datetime[0], "time":self.datetime[1]});
                    gen.endElement("timestamp"); gen.characters("\n")
                else:
                    # other attribute
                    gen.startElement(attr,{});
                    gen.characters(getXMLvalue(self, attr));
                    gen.endElement(attr); gen.characters('\n')

            gen.endElement("blogentry")
            gen.endDocument()
            outf.commit()
            os.chmod(outf.name, FILEPROT)
        except EnvironmentError,x:
            raise StorageError(str(x))
        
    def remove(self):
        filename=self.determineFileName(self.getStoragePath(), self.datetime[0], self.id)
        log.debug("remove BlogEntry %d file: %s" % (self.id,filename))
        os.remove(filename)
        super(BlogEntry,self).remove()
        
    def load(clazz, storageengine, datestr, Id):
        log.debug("loading BlogEntry %s/%d" % (datestr,Id))
        try:
            filename=clazz.determineFileName(storageengine.storagepath, datestr, Id)
            dom=xml.dom.minidom.parse(filename)
            return clazz._loadXML(storageengine, dom.documentElement)
        except EnvironmentError,x:
            raise StorageError(str(x))
    load=classmethod(load)
    
    def _loadXML(clazz, storageengine, rootnode):
        obj=object.__new__(clazz)
        obj._engine=storageengine
        if rootnode.attributes:
            obj.id=int(rootnode.attributes["id"].nodeValue)
        for child in rootnode.childNodes:
            if child.nodeType==xml.dom.Node.ELEMENT_NODE:
                if child.nodeName=="timestamp":
                    obj.datetime = (str(child.attributes["date"].nodeValue), str(child.attributes["time"].nodeValue))
                elif child.nodeName=="allowcomments":
                    obj.allowcomments = child.firstChild.nodeValue.lower() == "true"
                elif child.nodeName=="smileys":
                    obj.smileys = child.firstChild.nodeValue.lower() == "true"
                elif child.nodeName=="lastedited":
                    obj.lastedited = int(child.firstChild.nodeValue)
                elif child.nodeName=="numedits":
                    obj.numedits = int(child.firstChild.nodeValue)
                elif child.nodeName=="category":
                    obj.category = int(child.firstChild.nodeValue)
                else:
                    # other attribute.
                    if child.firstChild:
                        setattr(obj, child.nodeName, child.firstChild.nodeValue)
                    else:
                        setattr(obj, child.nodeName, None)
        return obj
    _loadXML=classmethod(_loadXML)

    def determineFileName(storagepath, datestr, entryid):
        return os.path.join(storagepath, datestr, "blogs", "%04d.xml" % entryid)
    determineFileName=staticmethod(determineFileName)


#
#   COMMENT     xml-storage-object
#
class Comment(_XMLObject):

    def store(self):
        self.makeId("comment")
        # comments are not loaded & stored by themselves, they are collected in Comments objects in the BlogEntry.

    def putInXML(self, xmlgen):
        xmlgen.startElement("comment",{"id":str(self.id)}); xmlgen.characters("\n")
        for attr in self.__slots__:
            if attr=="datetime":
                xmlgen.startElement("timestamp",{"date":self.datetime[0], "time":self.datetime[1]});
                xmlgen.endElement("timestamp"); xmlgen.characters("\n")
            elif attr=="author":
                xmlgen.startElement("author",{"name":self.author[0], "url":self.author[1] or "", "email":self.author[2] or "" });
                xmlgen.endElement("author"); xmlgen.characters("\n")
            else:
                # other attribute
                xmlgen.startElement(attr,{});
                xmlgen.characters(getXMLvalue(self, attr));
                xmlgen.endElement(attr); xmlgen.characters('\n')
        xmlgen.endElement("comment")
        xmlgen.characters("\n")
        
    def _loadXML(clazz, storageengine, rootnode):
        obj=object.__new__(clazz)
        obj._engine=storageengine
        if rootnode.attributes:
            obj.id=int(rootnode.attributes["id"].nodeValue)
        for child in rootnode.childNodes:
            if child.nodeType==xml.dom.Node.ELEMENT_NODE:
                if child.nodeName=="timestamp":
                    obj.datetime = (str(child.attributes["date"].nodeValue), str(child.attributes["time"].nodeValue))
                elif child.nodeName=="author":
                    obj.author = (child.attributes["name"].nodeValue, child.attributes["url"].nodeValue, child.attributes["email"].nodeValue)
                elif child.nodeName=="smileys":
                    obj.smileys = child.firstChild.nodeValue.lower() == "true"
                else:
                    # other attribute.
                    if child.firstChild:
                        setattr(obj, child.nodeName, child.firstChild.nodeValue)
                    else:
                        setattr(obj, child.nodeName, None)
        return obj
    _loadXML=classmethod(_loadXML)



#
#   COMMENTS     xml-storage-object
#
class Comments(_XMLObject):
    
    def store(self):
        self.id=self.blogid   # these comments belong to this blogentry id
        log.debug("storing Comments %s/%d" % (self.datetime[0],self.id))
        try:
            outf=TransactionalFile(Comments.determineFileName(self.getStoragePath(), self.datetime[0], self.id) , "wb")
            gen=XMLGenerator(out=outf, encoding="UTF-8")
            gen.startDocument()
            gen.startElement("comments",{"id":str(self.id)}); gen.characters("\n")
            for attr in self.__slots__:
                if attr=="datetime":
                    gen.startElement("timestamp",{"date":self.datetime[0], "time":self.datetime[1]});
                    gen.endElement("timestamp"); gen.characters("\n")
                elif attr=="comments":
                    gen.startElement("commentlist",{"count":str(len(self.comments))}); gen.characters("\n")
                    for comment in self.comments:
                        comment.store()
                        comment.putInXML(gen)
                    gen.endElement("commentlist"); gen.characters("\n")
                else:
                    # other attribute
                    gen.startElement(attr,{});
                    gen.characters(getXMLvalue(self, attr));
                    gen.endElement(attr); gen.characters('\n')

            gen.endElement("comments")
            gen.endDocument()
            outf.commit()
            os.chmod(outf.name, FILEPROT)
        except EnvironmentError,x:
            raise StorageError(str(x))
        
    def load(clazz, storageengine, datestr, Id):
        log.debug("loading Comments %s/%d" % (datestr,Id))
        try:
            filename=clazz.determineFileName(storageengine.storagepath, datestr, Id)
            if os.path.isfile(filename):
                dom=xml.dom.minidom.parse(filename)
                return clazz._loadXML(storageengine, Id, dom.documentElement)
            else:
                # file does not exist, return empty Comments class.
                obj=object.__new__(clazz)
                obj._engine=storageengine
                obj.id=obj.blogid=int(Id)
                # actually the datetime should be set identically to the datetime of
                # the blog entry this comments belongs to. But reading the entry just
                # to get the datetime is a bit slow, so we just put the date from the parameter
                # (which is most important, and MUST be correct!) and the current time in it,
                # until the comments are actually stored (then it is updated with the correct value)
                #  entry=BlogEntry.load(storageengine, datestr, Id)   # a bit slow, we need only the datetime of the article...
                #  obj.datetime=entry.datetime
                obj.datetime= (datestr, frog.util.isotimestr())
                obj.comments=[]
                obj.lastedited=0
                return obj
        except EnvironmentError,x:
            raise StorageError(str(x))
    load=classmethod(load)
    
    def _loadXML(clazz, storageengine, blogId, rootnode):
        obj=object.__new__(clazz)
        obj._engine=storageengine
        if rootnode.attributes:
            obj.id=obj.blogid=int(rootnode.attributes["id"].nodeValue)
        for child in rootnode.childNodes:
            if child.nodeType==xml.dom.Node.ELEMENT_NODE:
                if child.nodeName=="commentlist":
                    obj.comments=[]
                    for child in child.childNodes:
                        if child.nodeType==xml.dom.Node.ELEMENT_NODE and child.nodeName=="comment":
                            obj.comments.append( frog.objects.Comment._loadXML(storageengine, child) )
                elif child.nodeName=="timestamp":
                    obj.datetime = (str(child.attributes["date"].nodeValue), str(child.attributes["time"].nodeValue))
                elif child.nodeName=="lastedited":
                    obj.lastedited = int(child.firstChild.nodeValue)
                else:
                    # other attribute.
                    if child.firstChild:
                        setattr(obj, child.nodeName, child.firstChild.nodeValue)
                    else:
                        setattr(obj, child.nodeName, None)
        return obj
    _loadXML=classmethod(_loadXML)
    
    def remove(self):
        filename=self.determineFileName(self.getStoragePath(), self.datetime[0], self.id)
        log.debug("remove Comments %d file: %s" % (self.id,filename))
        os.remove(filename)
        super(Comments,self).remove()

    def determineFileName(storagepath, datestr, entryid):
        return os.path.join(storagepath, datestr, "comments", "%04d.xml" % entryid)
    determineFileName=staticmethod(determineFileName)

