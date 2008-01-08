#
#   Utilities for logging in using a cookie. ('remember me')
#   This is an Ypage base class. (The search page inherits from this class)
#

import hmac,zlib
import frog.util

import logging
log=logging.getLogger("Snakelets.logger")

SECRETKEY= 'b0zbd8da5e9*@!$d50qQYUx149af482{};123~]4c9@*$'  # XXX hardly secret
LOGINCOOKIE= 'FrogLoginCookie'


def deleteLoginCookie(page):
    page.delCookie(LOGINCOOKIE, path=frog.util.userURLprefix(page))
    
class CookieLogin:
    def sendLoginRememberCookie(self, login, password):
        cookie="USER=%s\0PASSWORD=%s" % (login, password)
        hash=hmac.new(SECRETKEY,cookie).hexdigest()
        cookie+="\0hash="+hash
        cookie=zlib.compress(cookie).encode('base-64').strip()
        self.setCookie(LOGINCOOKIE,cookie,path=frog.util.userURLprefix(self),maxAge=30*24*3600)
        
    def processLoginRememberCookie(self):
        logincookie=self.Request.getCookies().get(LOGINCOOKIE, None)
        if logincookie:
            logincookie=logincookie[0]
            try:
                cookie=zlib.decompress(logincookie.decode('base-64'))
                (cookie,hash) = cookie.split('\0hash=')
                if hmac.new(SECRETKEY,cookie).hexdigest() != hash:
                    raise ValueError("cookie invalid (hash)")
                (user,password) = cookie.split('\0')
                user=user[5:]
                password=password[9:]
                log.debug("user %s logs in with cookie" % user)
                self.Request.getContext().login=user
                self.Request.getContext().password=password
            except ValueError,x:
                deleteLoginCookie(self)
                log.warn("invalid login cookie discarded")

