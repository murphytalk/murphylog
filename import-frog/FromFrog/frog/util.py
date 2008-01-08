#
#   Various generic utility stuff, and BBcode/HTML processing.
#

import time, sre

def userURLprefix(page, userid=None):
    if userid:
        return page.URLprefix+"user/"+page.urlescape(userid)+"/"
    else:
        return page.URLprefix+"user/"+page.urlescape(page.SessionCtx.user.userid)+"/"

def articleURL(page, entry, alsoEditUrl=False):
    if type(entry) is tuple:
        url=userURLprefix(page)+"article/%s/%d" % entry
    else:
        url=userURLprefix(page)+"article/%s/%d" % (entry.datetime[0], entry.id)
    if not alsoEditUrl:
        return url
    return url, url+"?edit"

def userURLprefix_snakelet(snakelet, userid):
    return snakelet.getWebApp().getURLprefix()+"user/"+snakelet.urlescape(userid)+"/"
    
def articleURL_snakelet(snakelet, userid, entry):
    return userURLprefix_snakelet(snakelet, userid)+"article/%s/%d" % (entry.datetime[0], entry.id)

def commentURL(page, entry, comment, alsoEditUrl=False):
    url=articleurl=articleURL(page, entry)
    if comment.id:
        url+="#c"+str(comment.id)
    if not alsoEditUrl:
        return url
    editurl=articleurl+"?editcomment="+str(comment.id)
    return url, editurl

def archivedArticleURL(page, year, month, day, Id):
    # Id is currently ignored
    return userURLprefix(page)+"article/%04d-%02d-%02d"%(year,month,day)

def isotimestr(time=None, noseconds=True):
    if noseconds:
        return __formatdate("%H:%M", time, True)
    else:
        return __formatdate("%H:%M:%S", time, True)
    
def isodatestr(date=None):
    return __formatdate("%Y-%m-%d", date)

def shorttimestr(time=None):
    return __formatdate("%X", time, True)

def shortdatestr(date=None):
    return __formatdate("%x", date)

def mediumdatestr(date=None):
    return __formatdate("%d %b %Y",date)

def longdatestr(date=None):
    return __formatdate("%A, %d %b %Y", date)
    
def __formatdate(format,date,istime=False):
    if not date:
        return time.strftime(format)
    elif type(date) in (float, int):
        return time.strftime(format, time.localtime(date))
    elif type(date) in (tuple, time.struct_time):
        return time.strftime(format, date)
    elif type(date) is str:
        if istime:
            date=time.strptime(date,"%H:%M:%S")
        else:
            date=time.strptime(date[:10],"%Y-%m-%d")
        return time.strftime(format, date)
    else:
        raise TypeError("date/time is of invalid type")

def parseDateTime(datetimetuple):
    return time.mktime(time.strptime("%s %s" % datetimetuple, "%Y-%m-%d %H:%M"))
   
def fixTextareaText(text):
    if text:
        # textareas usually submit newlines as CR+LF, convert to a single LF
        return text.replace("\r\n","\n")
    return None


def validEmailAddr(email):
    return len(email)>=5 and '@' in email

def isSpider(useragent):
    # check for spiders, see http://www.iplists.com/nw/ for a list 
    return sre.search("wget|libcurl|bot|zoek|search.msn|scooter|crawl|spider|lycos|yahoo|inktomi|slurp|zyborg|google|askjeeves|teoma|excite|ilse|infoseek|intelli|cfetch", useragent, sre.IGNORECASE) is not None


import frog.text.default

content2html = frog.text.default.content2html
contentcleanup = frog.text.default.contentcleanup

