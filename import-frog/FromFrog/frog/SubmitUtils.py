#
# Utilities for processing the article submission.
# (the submit page inherits from this class)
#

import frog.objects, frog
import types, time
from frog.storageerrors import StorageError


import logging
log=logging.getLogger("Snakelets.logger")

class Submit:
    def prefillFormValues(self,form):
        self.RequestCtx.formValues={}
        for key in form.keys():
            value=form[key]
            if type(value) in types.StringTypes:
                self.RequestCtx.formValues[key]=value.strip()
        self.RequestCtx.formErrors={}
        
    def cleanup(self):
        if hasattr(self.SessionCtx,"currentEntry"):
            del self.SessionCtx.currentEntry
        if hasattr(self.SessionCtx,"entryToDelete"):
            del self.SessionCtx.entryToDelete
                
    def process(self,user):
        self.Request.setEncoding("UTF-8")
        form=self.Request.getForm()
        self.prefillFormValues(form)
        
        action=form.get("action")
        if action and self.Request.getSession().isNew():
            self.abort("Session is invalid. Have (session-)cookies been disabled?")

        # check if form submission really is allowed
        if action:
            if not self.User or not self.User.hasPrivilege(frog.USERPRIV_BLOGGER):
                self.abort("you're not allowed to submit articles")
        
        if action=="submit":
            if form.get("cancel-article"):
                self.cleanup()
                self.Yhttpredirect(frog.util.userURLprefix(self))
            elif form.get("submit-article") or form.get("update-article") or form.get("preview-article"):
                env={"urlprefix": self.URLprefix, "userid": user.userid}
                title=form.get("title","").strip()
                text2=frog.util.fixTextareaText(form.get("text2"))
                text2=frog.util.contentcleanup(text2,env)
                category=form.get("category")
                articletype=form.get("articletype")
                text=form.get("text")  
                # text can be a list because there are 2 textareas for the main text
                if type(text) is list:
                    if articletype=="normal":
                        text=text[0]  # first textarea
                    elif articletype=="split":
                        text=text[1]  # second textarea
                self.RequestCtx.formValues["text"]=text
                text=frog.util.fixTextareaText(text)
                text=frog.util.contentcleanup(text,env)
                if not text2:
                    articletype="normal"
                if articletype=="normal":
                    text2=None
                
                allowcomments=form.get("allowcomments","").lower()=="true"
                smileys=form.get("smileys","").lower()=="true"

                if not category:
                    self.RequestCtx.formErrors["category"]="required"
                if not title:
                    self.RequestCtx.formErrors["title"]="required"
                if not text:
                    self.RequestCtx.formErrors["text"]="required"
                if not self.RequestCtx.formErrors:
                    log.debug("no form errors")
                    category=int(category)
                    try:
                        if form.get("submit-article"):
                            log.debug("create new article")
                            self.SessionCtx.storageEngine.createBlogDirsForToday() # make sure the right directories exist
                            entry = frog.objects.BlogEntry(self.SessionCtx.storageEngine, user.categories[category], title, text, text2, articletype, allowcomments, smileys)
                            entry.store()
                            user.categories[category].count+=1
                            user.store()
                            log.info("created new article, id=%d" % entry.id)

                        elif form.get("update-article"):
                            log.debug("Update existing article")
                            entry=self.SessionCtx.currentEntry
                            if entry.category != category:
                                # update category counts
                                user.categories[entry.category].count-=1
                                user.categories[category].count+=1
                                user.store()
                            entry.category=category
                            entry.title=title
                            entry.text=text
                            entry.text2=text2
                            entry.articletype=articletype
                            entry.allowcomments=allowcomments
                            entry.smileys=smileys
                            entry.numedits+=1
                            entry.lastedited=int(time.time())
                            entry.store()
                            log.info("updated article, id=%d" % entry.id)
                        
                        elif form.get("preview-article"):
                            entry = frog.objects.BlogEntry(self.SessionCtx.storageEngine, user.categories[category], title, text, text2, articletype, allowcomments, smileys)
                            self.RequestCtx.previewArticle=entry
                            log.debug("preview set")
                            return
                            
                        self.WebApp.getSnakelet("articlestats.sn").updateStats(self.User.userid)    # update stats for this user
                        self.RequestCtx.article=entry
                        self.RequestCtx.status="submitted"
                        self.cleanup()
                        self.Yredirect("statusmessage.y")
                    except StorageError,x:
                        log.error("storing article failed: "+str(x))
                        self.RequestCtx.formErrors["_general"]="Failed to store your article. Please try again. If this error persists, please contact an administrator."

            elif form.get("delete-article"):
                entry=self.SessionCtx.currentEntry
                log.debug("deleting article %s/%d" % (entry.datetime, entry.id))
                self.RequestCtx.article=entry  # for status message
                commentCount = self.SessionCtx.storageEngine.getNumberOfComments(entry.datetime[0], entry.id)            
                del self.SessionCtx.currentEntry
                if commentCount>0:
                    # cannot delete; there are comments to this article
                    self.SessionCtx.entryToDelete = entry
                    self.RequestCtx.status="cannotdelete"
                    self.Yredirect("statusmessage.y")
                else:
                    self.removeArticle(entry,user)
            elif form.get("delete-article-and-all-comments"):
                entry=self.SessionCtx.entryToDelete
                log.debug("deleting article, and all comments %s/%d" % (entry.datetime, entry.id))
                self.RequestCtx.article=entry  # for status message
                comments = frog.objects.Comments.load(self.SessionCtx.storageEngine, entry.datetime[0], entry.id)
                log.info("Removing all comments for entry id "+str(entry.id))
                comments.remove()
                self.removeArticle(entry, user)
            else:
                self.abort("invalid or no action")

    def removeArticle(self, entry, user):
        log.debug("actually deleting article now; id="+str(entry.id))
        entry.remove()
        user.categories[entry.category].count-=1
        user.store()
        self.WebApp.getSnakelet("articlestats.sn").updateStats(self.User.userid)    # update stats for this user
        self.cleanup()
        self.RequestCtx.status="deleted"
        self.Yredirect("statusmessage.y")
    
    def prepareEditBlogEntry(self, fromSession=False):
        if self.User:
            log.debug("edit mode; user="+self.User.userid)
        else:
            log.debug("edit mode; not logged in")
        if hasattr(self.SessionCtx,"currentEntry") and (fromSession or self.Request.getParameter("action")):
            log.debug("getting entry from session")
            entry = self.SessionCtx.currentEntry
            date=entry.datetime[0]
            Id=entry.id
        else:
            log.debug("getting date(+id) from req params")
            date = self.Request.getParameter("date")
            Id = int(self.Request.getParameter("id"))
            entry=None
            
        if not entry:
            try:
                log.debug("loading article %s/%d" % (date,Id))
                entry = frog.objects.BlogEntry.load(self.SessionCtx.storageEngine, date, Id)
                self.SessionCtx.currentEntry = entry
                log.debug("loading comment count")
                self.SessionCtx.commentCount = self.SessionCtx.storageEngine.getNumberOfComments(entry.datetime[0], entry.id)
            except StorageError,x:
                self.abort("cannot load article with id "+str(Id))
    
        return entry
