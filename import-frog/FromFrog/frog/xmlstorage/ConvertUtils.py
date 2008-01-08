#
#   Utility functions to help with converting old blog data
#   to new Frog versions.
#

import os, time
import xml.dom
from frog import STORAGE_FORMAT, FILEPROT, DIRPROT
from frog.xmlstorage.ids import IDGenerator
from frog.xmlstorage.objects import XMLStorageEngine
import frog.objects

import logging
log=logging.getLogger("Snakelets.logger")


#
#   Scan a user data file to see what version it is
#
def scanVersion(storageEngine, userid):
    filename = frog.objects.User.determineFileName(storageEngine.makeStoragePath(userid))
    rootnode = xml.dom.minidom.parse(filename)
    nodes=rootnode.getElementsByTagName("version")
    if nodes:
        return nodes[0].firstChild.nodeValue
    return None



#
#   Find a suitable converter class (ADD NEW VERSIONS HERE)
#
def getConverter(existingVersion):
    log.debug("GETTING CONVERTER FROM [%s]" % existingVersion)
    if existingVersion==Convert_10_11.FROMVERSION:
        return Convert_10_11()
    if existingVersion==Convert_11_12.FROMVERSION:
        return Convert_11_12()
    if existingVersion==Convert_12_14.FROMVERSION:
        return Convert_12_14()
    if existingVersion==Convert_13_14.FROMVERSION:
        return Convert_13_14()
    if existingVersion==Convert_14_15.FROMVERSION:
        return Convert_14_15()
    if existingVersion==Convert_15_16.FROMVERSION:
        return Convert_15_16()
    return None

#
#   Generic converter base code
#
class ConverterBase(object):
    def __init__(self):
        self.errors=[]
    def convert(self, page, storageEngine):
        log.info("--- STARTING CONVERSION")
        page.write("<p>Converting from "+self.FROMVERSION+" to "+self.TARGETVERSION+" &hellip;</p>")
        users=storageEngine.listUsers(False)
        self.webapp=storageEngine.webapp
        page.write("<p>")
        while True:
            try:
                user=users.pop()
            except KeyError:
                break
            else:
                page.write(page.escape(user)+" &hellip; &nbsp; ")
                storageEngine = XMLStorageEngine(self.webapp, user)
                log.debug("----CONVERT USER "+user)
                try:
                    self.convertUser(page, storageEngine, user)   # implement in sub class
                    log.debug("----DONE")
                except Exception,x:
                    msg= "[ERROR: %s (%s)] " % (x.__class__,x)
                    page.write(msg)
                    self.errors.append(msg)
                    log.error("error occured; this account may be corrupt!!  "+msg)
                    
        page.write("</p>")
        log.info("--- CONVERSION FINISHED")

    def refreshUserCategories(self, storageEngine, user):
        # refresh category list for this user
        if self.TARGETVERSION == STORAGE_FORMAT:
            log.debug("refresh user category list...")
            userObj = frog.objects.User.load(storageEngine, user)
            if userObj.version!=self.TARGETVERSION:
                raise ValueError("version mismatch")
            userObj.refreshCategories()

            # (re)set category id to highest found id
            categoryId=max(userObj.categories.keys()) # highest cat id
            log.debug("updating id file; last category id="+str(categoryId))
            storagepath = storageEngine.makeStoragePath(user)
            idgen = IDGenerator(storagepath)
            idgen.ids["category"]=categoryId
            idgen.store()

            log.debug("refresh user category list done")

    def bumpVersionNumber(self, userFile):
        # bump the version number in the user.xml
        rootnode = xml.dom.minidom.parse(userFile)
        version = rootnode.getElementsByTagName("version")[0]
        newver=rootnode.createTextNode( self.TARGETVERSION )
        version.replaceChild(newver,version.firstChild)
        newfile = open(userFile,"wb")
        newfile.write(rootnode.toxml("UTF-8"))
        newfile.close()
        os.chmod(userFile, FILEPROT)


#
#   CONVERTER:  1.0 --> 1.1
#
class Convert_10_11(ConverterBase):
    FROMVERSION = "Frog 1.0"
    TARGETVERSION = "Frog 1.1"
    def convertUser(self, page, storageEngine, user):
        # update all version numbers
        log.debug("bump version number")
        storagepath = storageEngine.makeStoragePath(user)
        filename = frog.objects.User.determineFileName(storagepath)

        # add a new customization item (usepuzzles)
        rootnode = xml.dom.minidom.parse(filename)
        usepuzzles = rootnode.createElement("usepuzzles")
        usepuzzles.appendChild(rootnode.createTextNode("True"))
        rootnode.firstChild.insertBefore(usepuzzles, rootnode.firstChild.firstChild)
        newfile = open(filename,"wb")
        newfile.write(rootnode.toxml("UTF-8"))
        newfile.close()
        os.chmod(filename, FILEPROT)

        # for all articles: convert lastedited to timestamp
        log.debug("convert lastedited to timestamp")
        allentries = storageEngine.listAllBlogEntries()
        for (date,entryid) in allentries:
            filename = frog.objects.BlogEntry.determineFileName(storageEngine.storagepath,date,entryid)
            if os.path.isfile(filename):
                rootnode = xml.dom.minidom.parse(filename)
                lastedited = rootnode.getElementsByTagName("lastedited")
                if lastedited:
                    lastedited=lastedited[0]
                    if lastedited.firstChild:
                        mtime = int(time.mktime(time.strptime(lastedited.firstChild.nodeValue+" 12","%d %b %Y %H")))
                        newnode=rootnode.createTextNode( str(mtime) )
                        lastedited.replaceChild(newnode,lastedited.firstChild)
                    else:
                        lastedited.appendChild(rootnode.createTextNode("0"))
                    newfile = open(filename,"wb")
                    newfile.write(rootnode.toxml("UTF-8"))
                    newfile.close()
                    os.chmod(filename, FILEPROT)

        # add lastedited timestamp to all comments files
        log.debug("add lastedited timestamp to all comments files")
        for (date,entryid) in allentries:
            filename = frog.objects.Comments.determineFileName(storageEngine.storagepath,date,entryid)
            if os.path.isfile(filename):
                rootnode = xml.dom.minidom.parse(filename)
                comments=rootnode.getElementsByTagName("comment")
                if comments:
                    lastcommenttimestamp=comments[-1].getElementsByTagName("timestamp")[0]
                    datetime = "%s %s" % (lastcommenttimestamp.attributes["date"].nodeValue, lastcommenttimestamp.attributes["time"].nodeValue)
                    mtime = int(time.mktime(time.strptime(datetime,"%Y-%m-%d %H:%M")))
                    lastedited = rootnode.createElement("lastedited")
                    lastedited.appendChild(rootnode.createTextNode(str(mtime)))
                    rootnode.firstChild.insertBefore(lastedited, rootnode.firstChild.firstChild)
                    newfile = open(filename,"wb")
                    newfile.write(rootnode.toxml("UTF-8"))
                    newfile.close()
                    os.chmod(filename, FILEPROT)
        
        self.bumpVersionNumber(frog.objects.User.determineFileName(storagepath))

        # rebuild category list
        self.refreshUserCategories(storageEngine, user)


#
#   CONVERTER:  1.1 --> 1.2
#
class Convert_11_12(ConverterBase):
    FROMVERSION = "Frog 1.1"
    TARGETVERSION = "Frog 1.2"

    def changeProtection(self, root):
        log.debug("changing protection modes in "+root)
        for root, dirs, files in os.walk(root):
            for d in dirs:
                fullpath=os.path.join(root,d)
                os.chmod(fullpath, DIRPROT)
            for f in files:
                fullpath=os.path.join(root,f)
                os.chmod(fullpath, FILEPROT)

    def convertUser(self, page, storageEngine, user):
        storagepath = storageEngine.makeStoragePath(user)
        filename = frog.objects.User.determineFileName(storagepath)
        
        # change the protection modes of all blog dirs and files
        self.changeProtection(self.webapp.getConfigItem("storage"))
        self.changeProtection(self.webapp.getConfigItem("files"))

        log.debug("bump version number")
        self.bumpVersionNumber(filename)
        self.refreshUserCategories(storageEngine, user)


#
#   CONVERTER:  1.2 --> 1.4
#   Actually does very little, because 1.4 is expected
#   to be the final storage format. So it makes sense to make "1.4" the
#   storage format used in the Frog 1.4 data files.
#
class Convert_12_14(ConverterBase):
    FROMVERSION = "Frog 1.2"
    TARGETVERSION = "1.4"

    def convertUser(self, page, storageEngine, user):
        storagepath = storageEngine.makeStoragePath(user)
        filename = frog.objects.User.determineFileName(storagepath)
        
        log.debug("bump version number")
        self.bumpVersionNumber(filename)
        self.refreshUserCategories(storageEngine, user)

        # for all articles: add articletype=normal and empty text2 tag (to deal with new split article type)
        # also add mailoncomment=False (update: this flag is actually no longer used since Frog 1.5!! so we don't add it anymore)
        log.debug("add articletype=normal and empty text2 tag")
        allentries = storageEngine.listAllBlogEntries()
        for (date,entryid) in allentries:
            filename = frog.objects.BlogEntry.determineFileName(storageEngine.storagepath,date,entryid)
            if os.path.isfile(filename):
                rootnode = xml.dom.minidom.parse(filename)
                node = rootnode.createElement("text2")
                rootnode.firstChild.insertBefore(node, rootnode.firstChild.firstChild)
                node = rootnode.createElement("articletype")
                node.appendChild(rootnode.createTextNode("normal"))
                rootnode.firstChild.insertBefore(node, rootnode.firstChild.firstChild)
                # This flag is no longer used since 1.5 so we don't add it anymore:
                # node = rootnode.createElement("mailoncomment")
                # node.appendChild(rootnode.createTextNode("False"))
                # rootnode.firstChild.insertBefore(node, rootnode.firstChild.firstChild)
                newfile = open(filename,"wb")
                newfile.write(rootnode.toxml("UTF-8"))
                newfile.close()
                os.chmod(filename, FILEPROT)

# 1.3 format was the same as 1.2
class Convert_13_14(Convert_12_14):
    FROMVERSION = "1.3"
    TARGETVERSION = "1.4"

#
#   CONVERTER:  1.4 --> 1.5
#   new: the mailnotify, countreads, rssenabled, customfrontpage flags,
#        metakeywords, metadescription strings.
#
class Convert_14_15(ConverterBase):
    FROMVERSION = "1.4"
    TARGETVERSION = "1.5"

    def convertUser(self, page, storageEngine, user):
        storagepath = storageEngine.makeStoragePath(user)
        filename = frog.objects.User.determineFileName(storagepath)
        
        log.debug("bump version number")
        self.bumpVersionNumber(filename)
        self.refreshUserCategories(storageEngine, user)

        # add the new customization items
        rootnode = xml.dom.minidom.parse(filename)
        node = rootnode.createElement("countreads")
        node.appendChild(rootnode.createTextNode("True"))
        rootnode.firstChild.insertBefore(node, rootnode.firstChild.firstChild)
        node = rootnode.createElement("rssenabled")
        node.appendChild(rootnode.createTextNode("True"))
        rootnode.firstChild.insertBefore(node, rootnode.firstChild.firstChild)
        node = rootnode.createElement("mailnotify")
        node.appendChild(rootnode.createTextNode("False"))
        rootnode.firstChild.insertBefore(node, rootnode.firstChild.firstChild)
        node = rootnode.createElement("customfrontpage")
        node.appendChild(rootnode.createTextNode("False"))
        rootnode.firstChild.insertBefore(node, rootnode.firstChild.firstChild)
        node = rootnode.createElement("metadescription")
        rootnode.firstChild.insertBefore(node, rootnode.firstChild.firstChild)
        node = rootnode.createElement("metakeywords")
        rootnode.firstChild.insertBefore(node, rootnode.firstChild.firstChild)

        # write back the user.xml
        newfile = open(filename,"wb")
        newfile.write(rootnode.toxml("UTF-8"))
        newfile.close()
        os.chmod(filename, FILEPROT)

        # the 'mailoncomment' flag that all articles have since
        # the previous version is not removed. It's just not used anymore





#
#   CONVERTER:  1.5 --> 1.6
#   new: user.smileys, user.smileycolor, user.commentsmileys and entry.smileys booleans.
#
class Convert_15_16(ConverterBase):
    FROMVERSION = "1.5"
    TARGETVERSION = "1.6"

    def convertUser(self, page, storageEngine, user):
        storagepath = storageEngine.makeStoragePath(user)
        filename = frog.objects.User.determineFileName(storagepath)
        
        log.debug("bump version number")
        self.bumpVersionNumber(filename)
        self.refreshUserCategories(storageEngine, user)

        # add the new customization items
        rootnode = xml.dom.minidom.parse(filename)
        node = rootnode.createElement("smileycolor")
        node.appendChild(rootnode.createTextNode("0"))
        rootnode.firstChild.insertBefore(node, rootnode.firstChild.firstChild)
        node = rootnode.createElement("smileys")
        node.appendChild(rootnode.createTextNode("False"))
        rootnode.firstChild.insertBefore(node, rootnode.firstChild.firstChild)
        node = rootnode.createElement("commentsmileys")
        node.appendChild(rootnode.createTextNode("True"))
        rootnode.firstChild.insertBefore(node, rootnode.firstChild.firstChild)

        # write back the user.xml
        newfile = open(filename,"wb")
        newfile.write(rootnode.toxml("UTF-8"))
        newfile.close()
        os.chmod(filename, FILEPROT)

        # for all articles: add smileys=False
        log.debug("add smileys=False tags to articles")
        allentries = storageEngine.listAllBlogEntries()
        for (date,entryid) in allentries:
            filename = frog.objects.BlogEntry.determineFileName(storageEngine.storagepath,date,entryid)
            if os.path.isfile(filename):
                rootnode = xml.dom.minidom.parse(filename)
                node = rootnode.createElement("smileys")
                node.appendChild(rootnode.createTextNode("False"))
                rootnode.firstChild.insertBefore(node, rootnode.firstChild.firstChild)
                newfile = open(filename,"wb")
                newfile.write(rootnode.toxml("UTF-8"))
                newfile.close()
                os.chmod(filename, FILEPROT)

        # add smileys=False to all comments in all comments files
        log.debug("add smileys=False to all comments in all comments files")
        for (date,entryid) in allentries:
            filename = frog.objects.Comments.determineFileName(storageEngine.storagepath,date,entryid)
            if os.path.isfile(filename):
                rootnode = xml.dom.minidom.parse(filename)
                comments=rootnode.getElementsByTagName("comment")
                if comments:
                    for commentnode in comments:
                        node = rootnode.createElement("smileys")
                        node.appendChild(rootnode.createTextNode("False"))
                        commentnode.insertBefore(node, commentnode.firstChild)
                    newfile = open(filename,"wb")
                    newfile.write(rootnode.toxml("UTF-8"))
                    newfile.close()
                    os.chmod(filename, FILEPROT)

