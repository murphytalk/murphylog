#
#   Utilities for processing the account customization forms. In the form of
#   an Ypage base class. (The article page inherits from this class)
#

import frog.util
import sre,copy

import logging
log=logging.getLogger("Snakelets.logger")

class DoneNothing(Exception): pass


class Customize:

    def process(self):
        user=copy.copy(self.User) # work on a copy

        try:
            self.__process(user)
            # We have an updated user object.
            # Log in again with the new object, and also replace the
            # blog user object on the session context (if it's the same!)
            self.Request.getSession().loginUser(user)
            if user.userid==self.SessionCtx.user.userid and user.accounttype==frog.ACCOUNTTYPE_BLOGGER:
                self.User = self.SessionCtx.user = user
        except DoneNothing:
            return
        except EnvironmentError,x:
            log.error("Error storing user data: "+str(x))
            self.RequestCtx.formErrors["_general"]="Error storing user data, please try again"
            
    def __process(self,user):
        self.Request.setEncoding("UTF-8")
        if self.Request.getSession().isNew():
            self.abort("Session is invalid. Have (session-)cookies been disabled?")
        form=self.Request.getForm()
        self.RequestCtx.formErrors={}
        self.RequestCtx.formMessage=None
        action=form.get("action")
        if action=="updatetexts":
            pagetitle=form.get("pagetitle","")
            if pagetitle:
                user.displaystrings["pagetitle"]=pagetitle
                user.displaystrings["subtitle"]=form.get("subtitle","")
                user.displaystrings["menutext"]=form.get("menutext","")
                user.displaystrings["footertext"]=form.get("footer","")
                user.metakeywords=form.get("metakeywords","")
                user.metadescription=form.get("metadescription","")
                user.colorstyle=int(form.get("colorstyle",0))
                user.smileycolor=int(form.get("smileycolor",0))
                user.searchenabled=form.get("searchenabled","").lower()=="true"
                user.showlogin=form.get("showlogin","").lower()=="true"
                user.onlyregisteredcommenting=form.get("onlyregisteredcommenting","").lower()=="true"
                user.mailnotify=form.get("mailnotify","").lower()=="true"
                user.usepuzzles=form.get("usepuzzles","").lower()=="true"
                user.countreads=form.get("countreads","").lower()=="true"
                user.rssenabled=form.get("rssenabled","").lower()=="true"
                user.commentsmileys=form.get("commentsmileys","").lower()=="true"
                user.smileys=form.get("smileys","").lower()=="true"
                user.customfrontpage=form.get("customfrontpage","").lower()=="true"
                user.store()
                self.RequestCtx.formMessage="Strings stored"
            else:
                self.RequestCtx.formErrors["pagetitle"]="this field is required"
            
        elif action=="updateaccount":
            pw1=form.get("password1")
            pw2=form.get("password2")
            pwchange=False
            if pw1:
                if pw2!=pw1:
                    self.RequestCtx.formErrors["password2"]="not the same"
                    self.RequestCtx.formErrors["_general"]="Password not changed"
                else:
                    user.password=form["password1"]
                    pwchange=True
            user.email=form.get("email","")
            import frog.util
            if not frog.util.validEmailAddr(user.email):
                self.RequestCtx.formErrors["email"]="invalid email address"
                self.RequestCtx.formErrors["_general"]="problem with data"
                return
            user.name=form.get("name","")
            url=form.get("homepage","")
            if url and not url.lower().startswith("http://"):
                url="http://"+url
            user.homepage=url
            user.store()
            if pwchange:
                self.RequestCtx.formMessage="Account info stored, new password set."
            else:
                self.RequestCtx.formMessage="Account info stored."
            if form.get("forgetlogin",None):
                import frog.LoginUtils
                frog.LoginUtils.deleteLoginCookie(self)
                
        elif action=="categoryedit":
            if form.get("cat_remove"):
                cat=int(form.get("categories",0))
                if cat and cat in user.categories:
                    name = user.categories[cat].name
                    if len(user.categories)==1:
                        self.RequestCtx.formErrors["_general"]="Cannot remove last remaining category '%s'" % name
                    elif user.categories[cat].count>0:
                        self.RequestCtx.formErrors["_general"]="Cannot remove: there are still articles in category '%s'" % name
                    else:
                        del user.categories[cat]
                        user.store()
                        self.RequestCtx.formMessage="Removed category '%s'" % name
            elif form.get("cat_add"):
                cat=form.get("name",'')
                if cat:
                    for existingcat in user.categories.values():
                        if cat==existingcat.name:
                            self.RequestCtx.formErrors["_general"]="Category '%s' already exists" % cat
                            break
                    if not self.RequestCtx.formErrors:
                        user.addNewCategory(cat)
                        self.RequestCtx.formMessage="Added category '%s'" % cat
            elif form.get("cat_rename"):
                oldcatId=int(form.get("categories",0))
                if oldcatId and oldcatId in user.categories:
                    newname=form.get("name",'')
                    if newname:
                        oldname = user.categories[oldcatId].name
                        user.renameCategory(oldcatId, newname)
                        self.RequestCtx.formMessage="Renamed category '%s' to '%s'" % (oldname, newname)
            elif form.get("cat_rebuildstats"):
                user.refreshCategories()
                self.RequestCtx.formMessage="Category list has been rebuilt."
    
        elif action=="linksedit":
            if form.get("link_remove"):
                name=form.get("links",'')
                if name:
                    del user.links[name]
                    user.store()
                    self.RequestCtx.formMessage="Removed the link '%s'." % name
            elif form.get("link_add"):
                name=form.get("name",'')
                url=form.get("url",'')
                if name:
                    # if the name exists, just overwrite the old entry
                    if not url:
                        self.RequestCtx.formErrors["_general"]="You must type an URL for the link"
                    else:
                        if url and not url.lower().startswith("http://"):
                            url="http://"+url
                        user.links[name]=url
                        user.store()
                        self.RequestCtx.formMessage="Added link '%s'" % name
            
        elif action:
            self.abort("invalid action: "+action)
        else:
            raise DoneNothing
