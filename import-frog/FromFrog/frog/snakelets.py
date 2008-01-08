#
#   Various Snakelet components.
#

import cgi,os,sys,types,glob,time,sets,sre,pickle
import email.Utils       

from snakeserver.snakelet import Snakelet
from snakeserver.webform import FormUploadedFile, FormFileUploadError

import frog.objects,frog
from frog.storageerrors import StorageError
from frog.xmlstorage.objects import XMLStorageEngine

import logging
log=logging.getLogger("Snakelets.logger")




#
#   This snakelet serves static files for a specific user.
#   It contains a bit of error checking to avoid url manipulation,
#   and more importantly: deeplinking protection using referer header.
#
class FileServ(Snakelet):

    def requiresSession(self):
        return self.SESSION_NOT_NEEDED

    def getDescription(self):
        return "serves static files"

    def serve(self, request, response):
        if not request.getReferer().startswith(request.getBaseURL()):
            # deeplink attempted (request without a referer header)
            if not self.getWebApp().getConfigItem("allowdeeplinks"):
                return response.sendError(403, "deeplinking not allowed")
        filePrefix=self.getWebApp().getConfigItem("files")
        filename = os.path.normpath(os.path.join(filePrefix, request.getPathInfo()[1:]))
        if not filename.startswith(filePrefix):
            return response.sendError(403) # avoid url-hacking
        try:
            if not filename.startswith(self.getWebApp().getConfigItem("files")):
                raise IOError("path manipulation denied")
            if not os.path.isfile(filename):
                raise IOError("is not a file")
            stats = os.stat(filename)
        except EnvironmentError,x:
            response.sendError(404, str(x))
            return
        else:
            # use Snakelets 1.38+ static file serv API
            self.getWebApp().serveStaticFile(filename, response, False)    # don't use response headers (such as nocache, content disposition)
    

class UserError(Exception): pass

#
#   This snakelet handles the selection of the user,
#   whose blog pages are requested.
#
#   It extracts the user name from the url (.../username/...)
#   and loads the user info on the session if it is not already
#   there. The User object is put in session.user 
#
class User(Snakelet):

    def requiresSession(self):
        return self.SESSION_WANTED

    def getDescription(self):
        return "selects and loads blog user"

    def serve(self, request, response):
       
        username = restpath = None
        split=request.getPathInfo().split('/',2)
        if len(split)>1:
            username=split[1]
        else:
            # missing / at end of url
            response.HTTPredirect(request.getRequestURLplain()+"/")
            return
        if len(split)>2:
            restpath=split[2]
            
        if not username or len(split)<=1:
            self.redirect(self.getWebApp().getURLprefix()+"index.y", request, response)
            return

        if not restpath and not request.getPathInfo().endswith('/'):
            # missing / at end of url
            response.HTTPredirect(request.getRequestURLplain()+"/")
            return
                                
        sess = request.getSessionContext()
        # check if we need to load the requested user
        try:
            if sess:
                if not hasattr(sess,"user") or sess.user.userid!=username:
                    sess.user=self.selectUser(username, request.getSession())
            else:
                # no session, store user on the request context.
                # XXX this is currently not done because all pages need a session! (which is good but also bad)
                # request.getContext().user=self.selectUser(username, request.getSession())
                self.abort("No session available to store user data on")  
        except UserError,x:
            response.sendError(404,str(x))
            return
                             
        if restpath.startswith("article/"):
            self.redirectToArticle(restpath, request, response)
            return
        elif restpath.startswith("category/"):
            self.redirectToCategory(restpath, request, response)
            return
        elif restpath.startswith("archive/"):
            self.redirectToArchive(restpath, request, response)
            return
                                         
        target=self.getWebApp().getURLprefix()+"blog/"+(restpath or "index.y")
        self.redirect(target, request, response)

    def selectUser(self, username, session):
        storageEngine=self.getAppContext().storageEngine
        log.info("selecting new user: "+username)
        if session:
            # remove previous user from the session, load new one
            sessionCtx=session.getContext()
            user=session.getLoggedInUser()
            if user and user.userid!=username:
                session.logoutUser()  # if somebody else was logged in, log them out!
            if hasattr(session,"storageEngine"):
                log.debug("removing previous storage engine")
                sessionCtx.storageEngine.close()
            try:
                # create a new storage engine instance for this user
                sessionCtx.storageEngine=storageEngine.createNew(username)
            except StorageError,x:
                log.error("cannot get storage engine: "+str(x))
                raise UserError("cannot find user")
            user = frog.objects.User.load(sessionCtx.storageEngine, username)
        else:
            # there is no session, so just load the user
            user=storageEngine.loadUser(username)

        if user.accounttype!=frog.ACCOUNTTYPE_BLOGGER:
            raise UserError("user doesn't have blogger account")
        log.info("User loaded: "+user.userid)

        loggedInUser= session.getLoggedInUser()
        if loggedInUser and (user.userid == loggedInUser.userid):
            # the already logged-in user switched to "her own page"
            # so give her blogger access. (and filemgr access)
            loggedInUser.privileges.add(frog.USERPRIV_BLOGGER)
            loggedInUser.privileges.add(frog.USERPRIV_FILEMGR)

        numentries = sessionCtx.storageEngine.countAllBlogEntries()
        total=0
        for cat in user.categories.values():
            total+=cat.count
        if total != numentries:
            log.info("user article count != global count, rescanning")
            user.refreshCategories()

        return user

    def redirectToArticle(self, pathinfo, request, response):
        split = pathinfo.split('/')
        if len(split)>=2:
            ctx=request.getContext()
            ctx.date=split[1]
            if len(split)>=3 and split[2]:
                # the specific article id has also been given, so set the id,
                # and redirect to the specific article.
                ctx.id=split[2]
                target=self.getWebApp().getURLprefix()+"blog/article.y"
            else:
                # no specific article id has been given, so go to the index page
                request.setArg("date") #... for a given date
                target=self.getWebApp().getURLprefix()+"blog/index.y"
            self.redirect(target, request, response)
        else:
            response.sendError(400)

    def redirectToCategory(self, pathinfo, request, response):
        split = pathinfo.split('/')
        if len(split)>=2 and split[1]:
            request.getContext().category=split[1]
            target=self.getWebApp().getURLprefix()+"blog/category.y"
            self.redirect(target, request, response)
        else:
            response.sendError(400)

    def redirectToArchive(self, pathinfo, request, response):
        split = pathinfo.split('/')
        if len(split)>=2:
            if split[1]:
                request.getContext().archive=split[1]
            else:
                request.getContext().archive="OLDER"
            target=self.getWebApp().getURLprefix()+"blog/archive.y"
            self.redirect(target, request, response)
        else:
            response.sendError(400)
        

#
#   Snakelet that is not directly accessed.
#   Instead, it registeres a few tasks with the scheduler that
#   need to be performed on regular intervals. (scan articles etc)
#
class ArticleStats(Snakelet):

    def init(self):
        ctx=self.getAppContext()
        ctx.blogentrydates={}   # user->list of date strings
        ctx.articlecounts={}    # user->amount of articles
        ctx.articlesinmonth={} # user->(year,month)-> (num, dict)
                               #...where dict=day->list-of-article ids
        ctx.registeredusers=sets.Set()  # a set of user ids
        ctx.registeredbloggerusers=sets.Set()  # a set of user ids
        ctx.activearticles={}   # user->list of active articles
        ctx.populararticles_views={}    # user->list of popular articles (views)
        ctx.populararticles_comments={} # user->list of popular articles (comments)
        ctx.articlereads={}     # user->dict of article read counts (article key->readcount)

        # ---- ARTICLE STATS UPDATER TASKS -----
        scheduler=self.getPlugin("SchedulerPlugin")
        start=0
        start+=2; interval=self.getWebApp().getConfigItem("articlecount_updateperiod")
        scheduler.addIntervalTask(self.scheduled_UpdateUserListAndArticleCount, "ArticleCount update", start, interval, scheduler.PM_SEQUENTIAL, [])
        start+=2; interval=self.getWebApp().getConfigItem("blogentrydate_updateperiod")
        scheduler.addIntervalTask(self.scheduled_UpdateBlogEntryDates, "BlogEntry dates scanner", start, interval, scheduler.PM_SEQUENTIAL, [])
        start+=2; interval=self.getWebApp().getConfigItem("articlesinmonth_updateperiod")
        scheduler.addIntervalTask(self.scheduled_UpdateArticlesInMonth, "Articles in month scanner", start, interval, scheduler.PM_SEQUENTIAL, [])
        start+=2; interval=self.getWebApp().getConfigItem("activearticles_updateperiod")
        scheduler.addIntervalTask(self.scheduled_UpdateActiveArticles, "Active articles scanner", start, interval, scheduler.PM_SEQUENTIAL, [])
        
    def requiresSession(self):
        return self.SESSION_NOT_NEEDED
        
    def getDescription(self):
        return "updates cached article data"

    def serve(self, request, response):
        response.getOutput().write("nothing here.")

    def updateStats(self, userid):
        log.info("update all stats for user "+userid)
        self.user_UpdateBlogEntryDates(userid)
        self.user_UpdateArticleCount(userid)
        now = time.localtime()
        self.updateArticlesInMonth(userid, now.tm_year, now.tm_mon)
        self.updateActiveArticles(userid)
        log.debug("update all stats done")

    def updateArticlesInMonth(self, userid, year, month):
        log.info("update articles in month for user %s month %d/%d" % (userid, year,month))
        self.user_updateArticlesInMonth(userid, year, month)
        log.debug("update done")

    def updateActiveArticles(self, userid):
        log.info("update active articles for user "+userid)
        self.user_UpdateActiveArticles(userid)
        log.debug("update done")
    

    # the following method is called from the Scheduler, to update the list of articles per month regularly.
    def scheduled_UpdateArticlesInMonth(self):
        log.info("(scheduled) updating articles in month")
        users=self.getAppContext().storageEngine.listUsers(False)   # also update the user list
        now=time.localtime()
        for userid in users:
            year,month=now.tm_year,now.tm_mon
            for i in range(self.getWebApp().getConfigItem("archivemenu_nummonths")):
                self.user_updateArticlesInMonth(userid, year, month)
                month-=1
                if month<=0:
                    month+=12
                    year-=1

    def user_updateArticlesInMonth(self, userid, year, month):
        path = os.path.join(self.getWebApp().getConfigItem("storage"),userid,("%04d-%02d-*"+os.path.sep+"blogs"+os.path.sep+"*.xml") % (year,month))
        articles=[ article.split(os.path.sep) for article in glob.glob( path ) ]
        articles=[ (article[-3],article[-1]) for article in articles ]
        numarticles=len(articles)
        monthly={}
        for date,file in articles:
            day=int(date.split('-')[2])
            Id=int(file.split('.')[0])
            monthly.setdefault(day,[]).append(Id)
        self.getAppContext().articlesinmonth.setdefault(userid,{})[year,month]=(numarticles, monthly)
    
    # the following method is called from the Scheduler, to update the user list and article counts regularly.
    def scheduled_UpdateUserListAndArticleCount(self):
        log.info("(scheduled) updating article counts")
        counts={}
        users=self.getAppContext().storageEngine.listUsers(False)   # also update the user list
        for userid in users:
            self.user_UpdateArticleCount(userid, counts)
            self.user_StoreArticleReadCounts(userid)
        self.getAppContext().articlecounts = counts

    def user_UpdateArticleCount(self, userid, counts=None):
        path = os.path.join(self.getWebApp().getConfigItem("storage"),userid,"*"+os.path.sep+"blogs"+os.path.sep+"*.xml")
        articles=glob.glob( path )
        if counts is not None:
            counts[userid] = len(articles)
        else:
            self.getAppContext().articlecounts[userid] = len(articles)

    def user_StoreArticleReadCounts(self, userid):
        try:
            counts = self.getAppContext().articlereads[userid]
        except KeyError:
            # article counts have not been read yet, so don't store anything
            return
        path = os.path.join(self.getWebApp().getConfigItem("storage"),userid)
        filename = os.path.join(path, "articlereads.pickle")
        pickle.dump(counts, open(filename,"wb"))

    # the following method is called from the Scheduler, to update the available dates of the user's entries. (sorted from recent to old)
    def scheduled_UpdateBlogEntryDates(self):
        log.info("(scheduled) updating blog entry dates")
        dates={}
        users=self.getAppContext().storageEngine.listUsers(False)   # also update the user list
        for userid in users:
            self.user_UpdateBlogEntryDates(userid, dates)
        self.getAppContext().blogentrydates = dates
                   
    def user_UpdateBlogEntryDates(self, userid, entrydates=None):
        path = os.path.join(self.getWebApp().getConfigItem("storage"),userid)
        dates = [ d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) ]
        dates.sort()
        dates.reverse()  # sorted from recent to old
        if entrydates is not None:
            entrydates[userid] = dates
        else:
            self.getAppContext().blogentrydates[userid] = dates

    # the following method is called from the Scheduler, to update the active article lists.
    def scheduled_UpdateActiveArticles(self):
        log.info("(scheduled) updating active articles")
        users=self.getAppContext().storageEngine.listUsers(False)   # also update the user list
        active={}
        for userid in users:
            self.user_UpdateActiveArticles(userid, active)
        self.getAppContext().activearticles = active
    

    def user_UpdateActiveArticles(self, userid, activeArticles=None):
        # XXX this implementation is very slow; it scans all article and comments xmls
        storageEngine=self.getAppContext().storageEngine.createNew(userid)
        active=storageEngine.listAllBlogEntries()
        sortlist=[]
        leregex=sre.compile("<lastedited>(\d+)</lastedited>")
        dtregex=sre.compile('<timestamp\s+date="([0-9-]+)"\s+time="([0-9:]+)"')
        
        for date,articleId in active:
            modtime_comments = modtime_article = datetime_article = 0

            # read the comments xml file and extract lastedited timestamp
            commentfile=frog.objects.Comments.determineFileName(storageEngine.storagepath, date, articleId)
            if os.path.isfile(commentfile):
                for line in open(commentfile):
                    match=leregex.search(line)
                    if match:
                        modtime_comments=int(match.group(1))
                        break

            # read the article xml file and extract lastedited timestamp
            articlefile=frog.objects.BlogEntry.determineFileName(storageEngine.storagepath, date, articleId)
            founditems=0
            if os.path.isfile(articlefile):
                datetime=None
                for line in open(articlefile):
                    match=leregex.search(line)
                    if match:
                        modtime_article=int(match.group(1))
                        founditems+=1
                    match=dtregex.search(line)
                    if match:
                        datetime=match.groups()
                        founditems+=1
                    if founditems==2:
                        if not modtime_article:
                            # use the article's creation date/time as modtime
                            datestr="%s %s" % datetime
                            modtime_article=time.mktime(time.strptime(datestr,"%Y-%m-%d %H:%M"))
                        break
        
            numcomments=storageEngine.getNumberOfComments(date, articleId)
            sortlist.append( (max(modtime_comments,modtime_article), numcomments, date, articleId) )
        
        sortlist.sort()
        sortlist=sortlist[-15:] # max 15 entries
        sortlist.reverse()      # most recent first.

        if activeArticles is not None:
            activeArticles[userid] = sortlist
        else:
            self.getAppContext().activearticles[userid] = sortlist

        

#
#   This snakelet handles the generation of RSS feeds.
#
#   It extracts the user name from the url (/feed/username/feed.rss).
#
class RSSFeeder(Snakelet):

    def requiresSession(self):
        return self.SESSION_NOT_NEEDED

    def getDescription(self):
        return "rss news feeds"

    def init(self):
        ctx=self.getAppContext()
        ctx.cachedrssfeeds={}   # user->(timestamp, rss feed xml)
        ctx.cachedrssfeeds_cat={}   # user->dict of cat_id --> (timestamp, rss feed xml) 

    def serve(self, request, response):
        username, feedtype = request.getRequestURLplain().split('/')[-2:]
        try:
            user=self.getAppContext().storageEngine.loadUser(username)
            if not user.rssenabled:
                response.sendError(404, "RSS feeds are disabled for this user")
                return
        except StorageError:
            response.sendError(404, "No such user")
            return

        updateperiod = self.getWebApp().getConfigItem("rssfeeds_updateperiod")-5
        ctx=self.getAppContext()
        cat_id = None
        if request.getParameter("cat"):
            cat_id = int(request.getParameter("cat"))
        if cat_id is not None:
            # feed for a specific category
            previous = ctx.cachedrssfeeds_cat.get(username,{}).get(cat_id)
            if previous:
                timestamp, rssxml = previous
                if time.time()-timestamp < updateperiod:
                    self.setHeaders(response)
                    response.getOutput().write(rssxml)
                    return 
            # not cached, or we should update.
            if feedtype.endswith(".rss"):
                rssxml=self.rss(user, request, response, cat_id=cat_id)
                self.setHeaders(response)
                response.getOutput().write(rssxml)
                # put the xml in the cache
                ctx.cachedrssfeeds_cat.setdefault(username,{}) [cat_id] = (time.time(), rssxml)
            else:
                # unkown feed type (we only support *.rss now)
                response.sendError(501)
        else:
            # general feed
            previous = ctx.cachedrssfeeds.get(username)

            if previous:
                timestamp, rssxml = previous
                if time.time()-timestamp < updateperiod:
                    self.setHeaders(response)
                    response.getOutput().write(rssxml)
                    return 

            # not cached, or we should update.
            if feedtype.endswith(".rss"):
                rssxml=self.rss(user, request, response)
                self.setHeaders(response)
                response.getOutput().write(rssxml)
                # put the xml in the cache
                ctx.cachedrssfeeds[username]=(time.time(), rssxml)
            else:
                # unkown feed type (we only support *.rss now)
                response.sendError(501)

    def rss(self, user, request, response, cat_id=None):
        timetolive = max(10, self.getWebApp().getConfigItem("rssfeeds_updateperiod")/60)   # minutes
        log.debug("Generating RSS feed XML; cat=%r" % cat_id)
        blogtitle=user.displaystrings["pagetitle"]+' - '+user.displaystrings["subtitle"]
        if cat_id is not None:
            blogdescription=("The latest articles in category '%s'. " % user.categories[cat_id].name )+blogtitle
        else:
            blogdescription="The latest articles on this blog. "+blogtitle

        rss=RSSFeed(blogtitle,
                    request.getBaseURL()+frog.util.userURLprefix_snakelet(self, user.userid),
                    blogdescription, "Copyright by "+user.name, timetolive)
        storageEngine = XMLStorageEngine(self.getWebApp(), user.userid)
        dates=storageEngine.listBlogEntryDates()
        if dates:
            SHOWAMOUNT=10
            entrycount=0
            for showdate in dates:
                entryids=storageEngine.listBlogEntries(showdate)
                entryids.reverse() # descending
                if cat_id is None:
                    entryids=entryids[:(SHOWAMOUNT-entrycount)]
                entries=[ frog.objects.BlogEntry.load(storageEngine, showdate, Id) for Id in entryids ]
                for entry in entries:
                    if cat_id is not None and entry.category != cat_id:
                        continue
                    timestamp=frog.util.parseDateTime(entry.datetime)
                    articleURL=request.getBaseURL()+frog.util.articleURL_snakelet(self, user.userid, entry)
                    rsstxt = "{category: "+user.categories[entry.category].name+"}  "+entry.text[:300]+"..."
                    rss.addItem( entry.title, articleURL, user.email, user.name, timestamp, rsstxt )
                    entrycount+=1
                if entrycount>=SHOWAMOUNT:
                    break
        log.debug("Generating RSS feed XML - DONE")
        return rss.toXML("UTF-8")

    def setHeaders(self, response):
        response.setContentType("text/xml")
        response.setEncoding("UTF-8")
        # do something smart with caching?
        # response.setHeader("pragma","???")
        # response.setHeader("cache-control","???")
        # response.setHeader("expires","???")
        
 
        
#
#   Class that is used to construct an RSS 2.0 feed with items in it.
#
class RSSFeed:
    def __init__(self, title, link, description, copyright, ttl=30):
        self.feedinfo= {"title":cgi.escape(title), "link":cgi.escape(link), "description":cgi.escape(description), "copyright":cgi.escape(copyright), "ttl": ttl} 
        self.items=[]
    def addItem(self, title, link, authoremail, authorname, pubdatetime, description):
        authoremail=authoremail or '<no email address>'
        authorname=authorname or '<no name>'
        self.items.append( {"title":cgi.escape(title), "link":cgi.escape(link), "description":cgi.escape(description),
                            "authoremail": cgi.escape(authoremail), "authorname":cgi.escape(authorname),
                            "pubdate": email.Utils.formatdate(pubdatetime, localtime=False, usegmt=True) } )
    def toXML(self, encodingname):
        self.feedinfo["encoding"]=encodingname
        self.feedinfo["builddate"]=email.Utils.formatdate(localtime=False, usegmt=True)
        XML=u"""<?xml version="1.0" encoding="%(encoding)s"?>
<rss version="2.0">
<channel>
 <title>%(title)s</title>
 <link>%(link)s</link>
 <description>%(description)s</description>
 <copyright>%(copyright)s</copyright>
 <lastBuildDate>%(builddate)s</lastBuildDate>
 <generator>Frog (Python)</generator>
 <category>Blog</category>
 <docs>http://blogs.law.harvard.edu/tech/rss</docs>
 <ttl>%(ttl)d</ttl>
"""
        XML=XML % self.feedinfo
        for item in self.items:
            itemXML=u"""<item>
 <title>%(title)s</title>
 <link>%(link)s</link>
 <description>%(description)s</description>
 <author>%(authoremail)s (%(authorname)s)</author>
 <pubDate>%(pubdate)s</pubDate>
</item>
"""
            XML += itemXML % item

        return XML+u"</channel>\n</rss>"
