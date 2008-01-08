#the following modules are from Zope
from StructuredText import ST
from StructuredText import DocumentClass
from StructuredText import StructuredText
from StructuredText import HTMLClass
from StructuredText.StructuredText import HTML
#the following module is from ZopeChinaPack 
import StructuredTextPak

def stx2html(txt):
    """
    render StructuredText to HTML
    """
    if txt is not None: 
        Doc  = DocumentClass.DocumentClass()
        HTML = HTMLClass.HTMLClass()
        text = Doc(ST.StructuredText(txt))
        return  HTML(text)
    else:
        return ''

if __name__=="__main__":
    import tempfile
    tmpdir=tempfile.gettempdir()
    f=open(tmpdir+'/stx.txt','rt')
    txt=f.read()
    f.close()
    f=open(tmpdir+'/stx.htm','wt')
    f.write(stx2html(txt))
    f.close()
