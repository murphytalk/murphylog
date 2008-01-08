#
#   The various data objects.
#   The storage aspects are implemented in a different module.
#
#
#   Every object has its own reference to the storage engine that is
#   used for that object. This way it is feasible to load and store objects
#   that belong to different users (and thus, may have different storage engines).
#
#   The __slots__ of an object will be written to the Persistent store.
#
import frog
import xmlstorage.objects as storageobjects
StorageEngine=storageobjects.XMLStorageEngine
import LoginUser
import util


__all__ = ["User","BlogEntry","Comment","Comments", "DEFAULT_CATEGORY_NAME"]


DEFAULT_CATEGORY_NAME = "general"


import logging
log=logging.getLogger("Snakelets.logger")



#
#   USER   (both a selected blogger user and logged in user)
#
class User(LoginUser.LoginUser, storageobjects.User):
    __slots__=['version','email','homepage','displaystrings','metakeywords','metadescription', 'categories','links',
               'accounttype','colorstyle','smileycolor', 'searchenabled','showlogin','onlyregisteredcommenting',
               'mailnotify', 'usepuzzles', 'countreads', 'rssenabled', 'customfrontpage', 'smileys', 'commentsmileys']
               # userid, name, passwd are not slots, but are explicitly added in the storageobject
    def __init__(self, storageengine, userid, password, accounttype, passwordhash=None, directory=None):
        LoginUser.LoginUser.__init__(self, userid, password, "", passwordhash=passwordhash, privileges=None)
        storageobjects.User.__init__(self, storageengine)
        if accounttype in (frog.ACCOUNTTYPE_BLOGGER, frog.ACCOUNTTYPE_LOGIN):
            self.accounttype=accounttype
        else:
            raise ValueError("invalid account type: "+accounttype)
        self.version=None
        self.displaystrings={}  # displaystringname-->string
        self.metakeywords = self.metadescription = ""
        self.categories={}      # map of catId-->Category object
        self.links={}           # name-->url
        self.email=self.homepage=""
        self.colorstyle=0
        self.smileycolor=0
        self.mailnotify = self.customfrontpage = self.smileys = False
        self.searchenabled = self.showlogin = self.onlyregisteredcommenting = \
                self.usepuzzles = self.countreads = self.rssenabled = self.commentsmileys = True
        if accounttype == frog.ACCOUNTTYPE_BLOGGER:
            # set the user's file directory, for filemgr.
            self.directory=directory
 
    def refreshCategories(self):
        # scan all blog entries and count the categories.
        # update the category list and store the user.
        cats = self.storage_determineCategoryCounts()    # in storage class.
        if cats:
            self.categories = cats
            self.store()
        else:
            # hmm, there are no categories left... create the default category.
            self.categories.clear()
            self.addNewCategory(DEFAULT_CATEGORY_NAME)
            return

    def getStorageEngine(self):
        return self._engine
        
    def addNewCategory(self, name, count=0):
        cat = Category(self._engine, name, count)
        cat.store()
        self.categories[cat.id] = cat
        self.store()
        return cat
    def renameCategory(self, oldcatId, newname):
        self.categories[oldcatId].name=newname
        self.store()
        

#
#   CATEGORY (embedded in USER object)
#
class Category(storageobjects.Category):
    __slots__=['name','count' ]
    def __init__(self, storageengine, name, count=0):
        super(Category,self).__init__(storageengine)
        if not name:
            raise ValueError("name may not be empty or none")
        self.name=name
        self.count=count
    def __cmp__(self, other):
        return cmp(self.name, other.name)   # comparison is by name (for sorting)
    def __eq__(self,other):
        return self.id==other.id
    def __ne__(self,other):
        return self.id!=other.id
    def __hash__(self):
        return hash( self.id )



#
#   BLOG ENTRY / ARTICLE
#           
class BlogEntry(storageobjects.BlogEntry):
    __slots__=['datetime', 'lastedited', 'numedits', 'category', 'articletype', 'title', 'text', 'text2',
               'allowcomments','smileys','texttype']
    #LM -> dtime and text_type added
    #text_type's possible values are: bbcode,structured
    def __init__(self, storageengine, category, title, text, text2=None, articletype="normal", allowcomments=True, smileys=False,dtime=None,texttype='bbcode'):
        super(BlogEntry,self).__init__(storageengine)
        if dtime is None:
            self.datetime =  util.isodatestr(), util.isotimestr()
        else:
            self.datetime =  dtime
        if not isinstance(category, Category):
            raise TypeError("category must be instance of Category")
        if not category.id:
            raise ValueError("category has no id")
        self.category=category.id
        self.title=title
        self.text=text
        self.text2=text2
        self.articletype=articletype
        self.allowcomments=allowcomments
        self.smileys=smileys
        self.lastedited=0
        self.numedits=0
        #LM -> new type
        self.texttype=texttype
    def countreads(self, increase=True, request=None):
        return self._engine.countReads(self, increase, request)
    def __cmp__(self, other):
        return cmp( (self.id, self.datetime), (other.id, other.datetime) )
    def __hash__(self):
        return hash( (self.id, self.datetime) )

#
#   COMMENT / REPLY TO ARTICLE (embedded in COMMENTS object)
#
class Comment(storageobjects.Comment):
    __slots__=['datetime', 'author', 'ipaddress', 'text', 'smileys' ]
    def __init__(self, storageengine, (authorname, authorurl, authoremail), ipaddress, text, smileys):
        super(Comment,self).__init__(storageengine)
        self.datetime = util.isodatestr(), util.isotimestr()
        self.author = authorname, authorurl, authoremail
        self.ipaddress=ipaddress or ""
        self.text=text
        self.smileys=smileys
    def __cmp__(self, other):
        return cmp( (self.id, self.datetime), (other.id, other.datetime) )
    def __hash__(self):
        return hash( (self.id, self.datetime) )


#
#   COMMENTS / list of COMMENT objects
#
class Comments(storageobjects.Comments):
    __slots__=['lastedited','datetime','comments']
    def __init__(self, storageengine, blogentry, comments):
        super(Comments,self).__init__(storageengine)
        self.blogid = blogentry.id
        self.datetime =  blogentry.datetime
        self.lastedited = 0
        self.comments=comments  # list of Comment objects
    def __cmp__(self, other):
        return cmp( (self.id, self.datetime), (other.id, other.datetime) )
    def __hash__(self):
        return hash( (self.id, self.datetime) )



def test():
    blogdata="E:\\Study\\PRJ\\FrogComplete-1.7\\blogdata"

    cat = 3

    se=StorageEngine(None, (tempfile.gettempdir(), "murphytalk") )
    se.createBlogDirsForToday()
    entry = BlogEntry(se,cat,title,"this is text1", "this is text2","split",True,True)
    entry.store()
    u=User(se, "murphytalk", "java2", "blogger")
    user.categories[cat].count+=1
    user.store()
#    se2=StorageEngine(None, (tempfile.gettempdir(), "harriet") )
#    se2.createBlogDirsForToday()
#
#    u=User(se1, "irmen", "geheim", "blogger")
#    cat1=u.addNewCategory("cat1")
#    u.store()
#    u=User(se2, "harriet", "geheim", "blogger")
#    cat2=u.addNewCategory("cat2")
#    u.store()
#    b=BlogEntry(se1, cat1, "de titel"+unichr(0x20ac), "dit is de tekst."+unichr(0x20ac))
#    b.store()
#    b_id1=b.id
#    print "BLOG ID1:",b_id1
#    b=BlogEntry(se1, cat1, "de titel2"+unichr(0x20ac), "dit is de tekst2."+unichr(0x20ac))
#    b.store()
#    b_id2=b.id
#    print "BLOG ID2:",b_id2
#    datestr=b.datetime[0]
#    c1=Comment(se1, ("Gekke Gerrit"+unichr(0x20ac),"http://bla"+unichr(0x20ac), "gerrit@foo.bar"), None, "dit is het commentaar."+unichr(0x20ac), False)
#    c1.store()
#    c_id1=c1.id
#    print "COMMENT ID1:",c_id1
#    c2=Comment(se1, ("Gekke Gerrit2"+unichr(0x20ac),"http://bla2"+unichr(0x20ac), "gerrit@foo.bar"), None, "dit is het commentaar2."+unichr(0x20ac), False)
#    c2.store()
#    c_id2=c2.id
#    print "COMMENT ID2:",c_id2
#    c=Comments(se1, b, [c1,c2] )
#    c.store()
#    cmts_id=c.id
#    print "COMMENTS ID:",cmts_id
#    
#    u=User.load(se1,"irmen")
#    print "user1 geladen:",u.id,u,u.name
#    print "cats:",u.categories
#    u.name="dinges"+unichr(0x20ac)
#    u.store()
#    print "user1 weer opgeslagen"
#    u=User.load(se2,"harriet")
#    print "user2 geladen:",u.id,u,u.name
#    u.name="dinges"+unichr(0x20ac)
#    u.store()
#    print "user2 weer opgeslagen"
#    b=BlogEntry.load(se1,datestr, b_id1)
#    print "b1 geladen",b.id,b.articletype
#    b.title="dinges"+unichr(0x20ac)
#    b.store()
#    print "b1 weer opgeslagen"
#    b=BlogEntry.load(se1,datestr, b_id2)
#    print "b2 geladen",b.id,b.articletype
#    b.title="dinges"+unichr(0x20ac)
#    b.store()
#    print "b2 weer opgeslagen"
#    c=Comments.load(se1, datestr, cmts_id)
#    print "cmts geladen",c.id,c.comments
#    c.store()
#    print "cmts weer opgeslagen"
#    c2=Comments.load(se1, datestr, cmts_id)
#    print "cmts geladen",c2.id,c2.comments
#    print "1e comment ook in andere lijst?",c2.comments[0] in c.comments
#    print "#=",len(c.comments)
#    c.comments.remove(c2.comments[0])
#    print "1e comment uit andere lijst gehaald"
#    print "1e comment ook in andere lijst?",c2.comments[0] in c.comments
#    print "#=",len(c.comments)
    
    
if __name__=="__main__":
    test()
