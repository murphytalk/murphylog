#
#   $Id: transactionalfile.py,v 1.4 2005/05/02 00:07:01 irmen Exp $
#
#   (c) Irmen de Jong.
#   This is open-source software, released under the MIT Software License:
#   http://www.opensource.org/licenses/mit-license.php
#

import os


class TransactionalFile(file):

    """This class attempts to be a file object with transactional
    properties. Writing initially goes to a temporary file instead
    of the target file directly.
    When you're done, you don't close() this file, but you
    commit() or rollback() the file.
    A commit() replaces the old file with the new file
    (using renaming, so should be quite safe and fast).
    When something happens that causes the commit not to be executed,
    such as an error, the file is automatically rollback-ed, and
    the original contents remain untouched.
    NOTE: this is NOT thread-safe!! Don't write the same file from
    within multiple threads, that will not work!"""

    def __init__(self, name, mode='wb', buffering=1):
        if mode not in ('w','wb'):
            raise ValueError("only accepting write mode")
        self.__name=name
        self.__tempname=name+"~"
        file.__init__(self, self.__tempname, mode, buffering)
        
    def __del__(self):
        self.rollback()

    def getName(self):
        return self.__name
    name=property(getName,None,None)
        
    def close(self):
        raise AttributeError("TransactionalFile must be closed using rollback() or commit()")
        # file.close(self)
        
    def rollback(self):
        if not self.closed:
            file.close(self)
            try:
                os.remove(self.__tempname)
            except EnvironmentError:
                pass
        
    def commit(self):
        if not self.closed:
            file.close(self)
            backup=self.__name+"@"
            if os.path.isfile(self.__name):
                try:
                    os.rename(self.__name, backup)
                except EnvironmentError,x:
                    os.remove(self.__tempname)
                    raise
            else:
                backup=None
            try:
                os.rename(self.__tempname, self.__name)
            except EnvironmentError,x:
                os.rename(backup, self.__name)
                raise
            else:
                if backup:
                    os.remove(backup)


def test():
    filename="/tmp/somefile.txt"
    content="The quick brown fox jumps over the lazy dog."
    print "Writing to file",filename
    r=TransactionalFile(filename,"wb")
    r.write(content+'\n')
    print "committing file."
    r.commit()
    print "done."
    print "Writing to file",filename
    r=TransactionalFile(filename,"wb")
    r.write("Scratch that!!!!\n")
    print "rollback file."
    r.rollback()
    print "The file should still contain the original content,"
    print "'%s'." % content

    

if __name__=="__main__":
    test()
 
