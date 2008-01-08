#
#   Utilities for processing the article search forms. In the form of
#   an Ypage base class. (The search page inherits from this class)
#

import frog.objects
import types, time
from frog.storageerrors import StorageError


import logging
log=logging.getLogger("Snakelets.logger")

class Search:
    def prefillFormValues(self,form):
    	self.RequestCtx.formValues={}
    	for key in form.keys():
    		value=form[key]
    		if type(value) in types.StringTypes:
    			self.RequestCtx.formValues[key]=value.strip()
    	self.RequestCtx.formErrors={}
    	self.RequestCtx.formMessage=None
    
    def validateSearchForm(self,form):
        if self.Request.getSession().isNew():
            self.abort("Session is invalid. Have (session-)cookies been disabled?")
        if form.get("fromdate"):
            try:
                fromdate = time.strptime(form["fromdate"],"%Y-%m-%d")
            except ValueError:
                self.RequestCtx.formErrors["dates"]="invalid date format(s)"
        if form.get("todate"):
            try:
                todate = time.strptime(form["todate"],"%Y-%m-%d")
            except ValueError:
                self.RequestCtx.formErrors["dates"]="invalid date format(s)"
        
    def readArticlesFromDate(self, storageEngine, date):
        entryids=storageEngine.listBlogEntries(date)
        entryids.reverse() # descending
        try:
            return [ frog.objects.BlogEntry.load(storageEngine, date, Id) for Id in entryids ]
        except StorageError,x:
            log.error("Error loading articles: "+str(x))
            self.abort("cannot load articles")
    
    def process(self):
        self.Request.setEncoding("UTF-8")
        form=self.Request.getForm()
        self.prefillFormValues(form)
        action=form.get("action")
    
        if action:
            self.validateSearchForm(form)

            # perform the actual search
            
            if form.get("title") or form.get("category") or form.get("text") or form.get("fromdate") or form.get("todate"):
                self.RequestCtx.searchResult=[]
                dates=self.SessionCtx.storageEngine.listBlogEntryDates()
                fromdate=form.get("fromdate","0000-00-00")
                todate=form.get("todate","9999-99-99")
                dates=[date for date in dates if date>=fromdate and date<=todate]
                for date in dates:
                    for article in self.readArticlesFromDate(self.SessionCtx.storageEngine, date):
                        found=True
                        if form.get("title"):
                            found &= form.get("title").upper() in article.title.upper()
                        if form.get("text"):
                            txt=(article.text + (article.text2 or "")).upper()
                            found &= form.get("text").upper() in txt
                        if form.get("category"):
                            found &= int(form.get("category")) ==  article.category
                        if found:
                            self.RequestCtx.searchResult.append(article)

