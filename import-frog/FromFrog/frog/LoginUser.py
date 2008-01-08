#############################################################################
#
#	$Id: user.py,v 1.17 2005/09/11 16:34:03 irmen Exp $
#	User management (authenticated users, roles).
#
#	This is part of "Snakelets" - Python Web Application Server
#	which is (c) Irmen de Jong - irmen@users.sourceforge.net
#
#############################################################################

#
# Notice that the user id is set once (when creating the user object) and cannot
# be changed, and that the password itself is not stored but its md5 hash instead.
#
# Privileges are stored and returned as a Set.
#

import md5, sets, time

class LoginUser(object):
    def getuserid(self): return self.__userid
    def getname(self): return self.__name
    def setname(self, name): self.__name=name
    def setpassword(self,passwd):
        if passwd:
            string = self.userid+passwd
            if type(string) is unicode:
                string=string.encode("UTF-8")
            self.__passwordhash=md5.new(string).digest()
        else:
            self.__passwordhash=None
    def getpassword(self): return self.__passwordhash
    def getprivileges(self): return self.__privileges
    def setprivileges(self, privs): self.__privileges=sets.Set(privs)
    def delprivileges(self): self.__privileges=sets.Set()
    
    userid=property(getuserid, None, None, "unique id")
    name=property(getname, setname, None, "descriptive name")
    password=property(getpassword,setpassword,None,"secret password. Only the md5 hash is stored, not the pw itself")
    privileges=property(getprivileges, setprivileges, delprivileges, "set of the privileges this user has")
    
    def __init__(self, userid, password=None, name=None, privileges=None, passwordhash=None):
        self.__userid=userid
        self.name=name
        if passwordhash:
            # To initialize the password hash from an external source
            # for instance when you're loading user data from a database
            self.__passwordhash = passwordhash    
        else:
            self.password=password
        self.privileges=privileges or []

    def checkPassword(self, password):
        string = self.userid+password
        if type(string) is unicode:
            string=string.encode("UTF-8")
        return md5.new(string).digest() == self.__passwordhash
    
    def hasPrivileges(self, privileges):
        # does this user have ALL of the asked privileges?
        return sets.Set(privileges).issubset(self.privileges)
    
    def hasAnyPrivilege(self, privileges):
        # does this user have any of the asked privileges?
        return len(sets.Set(privileges) & self.privileges)>0   # intersection

    def hasPrivilege(self, privilege):
        # does this user have the given privilege?
        return privilege in self.privileges

    def __repr__(self):
        return "<%s.%s object '%s' at 0x%08lx>" % (self.__module__, self.__class__.__name__, self.userid, id(self))
