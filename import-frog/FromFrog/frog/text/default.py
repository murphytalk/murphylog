#
#   Frog's default markup processor.
#
#   (note: called trough frog.util package, not directly)
#

import sre, urllib, urlparse, cgi, mimetypes, os, math
from frog.text.errors import MarkupSyntaxError

__all__=["contentcleanup","content2html"]


#   Called to 'clean up' entered content, before it is stored in the data store
def contentcleanup(text, environment={}):
    if text:
        return text.strip()
    else:
        return None


newlineRE = sre.compile(r'(?:\r?\n){2,}')
tokenizeRE = sre.compile(r'(.*?)\[(/?[^[]*?(?:=([^[]*))?)\]', sre.DOTALL)

SENTINEL = "/sentinel"


#
# The default markup text parser.
# env must contain:
#  "urlprefix" (the url prefix for links) 
#  "userid" (the current blog user id)
#  "filepath" (the root path where statically linked files are stored)
#  "smileys" (if smiley images should be used or not, must be the smiley color index or None)
#
# Not called externally, the content2html function is used instead.
#
class Parser:
    def __init__(self, env={}, comment=False):
        self.parsetree=[]
        self.inparagraph=False
        self.opentags=self.closetags=0
        self.environ=env
        self.comment=comment
        self.initialParagraph()
    def initialParagraph(self):
        self.openParagraph()  # normally, parsed blocks start with a new paragraph.
    def parse(self, matches, closetag=SENTINEL):
        for m in matches:
            txt,tag,extra=m.group(1,2,3)   # 'extra' is the text after a '=' in the tag (with url, for instance)
            if txt:
                txt=self.processText(txt)
                if txt:
                    self.parsetree.append( txt )
            if tag in ('b', 'i', 'tt'):
                self.parsetree.append("<%s>" % tag)
                self.opentags+=1
            elif tag in ('/b', '/i', '/tt'):
                self.parsetree.append("<%s>" % tag)
                self.closetags+=1
            elif tag=='u':
                self.parsetree.append('<span class="underlined">')
                self.opentags+=1
            elif tag=='/u':
                self.parsetree.append('</span>')
                self.closetags+=1
            elif tag=='center':
                self.closeParagraph(False)  # XXX a bit of a hack
                self.parsetree.append('<div style="text-align:center">')
                self.opentags+=1
            elif tag=='/center':
                self.parsetree.append('</div>')
                self.closetags+=1
                self.openParagraph(False)  # XXX a bit of a hack
            elif tag=='/':
                self.parsetree.append("<br />")      # line break
            #elif tag[0] in (" ","\t"):
            #    # ignore this tag, just add it as text.
            #    self.parsetree.append( '['+cgi.escape(tag)+']' )    # tags must not be processed
            elif tag.startswith("@:"):
                # article cross-link. Target is not checked!
                self.environ["articlelink"]=tag[2:]
                self.parsetree.append( '<a href="%(urlprefix)suser/%(userid)s/article/%(articlelink)s"><img alt="remote" src="%(urlprefix)simg/article.png" style="padding-bottom:0.5ex" />other article</a>' % self.environ )
            elif tag.startswith("@@"):
                # image forced download link (not embedded)
                filename=tag[2:].strip()
                self.environ["file"]=filename
                mime=mimetypes.guess_type(filename)
                if mime:
                    mime=mime[0] or ""
                stats=self.fileStats(filename)
                if stats:
                    self.environ["icon"]=self.getMimeIcon(mime)
                    self.environ["sizekb"]=int(math.ceil(stats.st_size / 1024.0))
                    self.environ["short"]=os.path.split(filename)[1]
                    self.parsetree.append( '<a href="%(urlprefix)sfiles/%(userid)s/%(file)s" title="Download file, %(sizekb)d Kb" rel="nofollow"><img alt="download" src="%(urlprefix)simg/%(icon)s" style="padding-bottom:0.5ex" />%(short)s</a>' % self.environ )
                elif filename[:5].lower() == "http:": # external link?
                    self.environ["icon"]=self.getMimeIcon(mime)
                    scheme,netloc,path,query,fragment = urlparse.urlsplit(filename)
                    self.environ["short"]=os.path.split( path ) [1] or filename
                    self.environ["netloc"]=netloc
                    self.parsetree.append( '<a href="%(file)s" title="Download file from %(netloc)s" rel="nofollow"><img alt="remote" src="%(urlprefix)simg/remote.gif" style="padding-bottom:0.5ex" /><img alt="download" src="%(urlprefix)simg/%(icon)s" style="padding-bottom:0.5ex" />%(short)s</a>' % self.environ )
                else:
                    self.parsetree.append( '[[!!! BAD LINK: %(file)s !!!]]' % self.environ)

            elif tag.startswith("@"):
                # 'smart' link/embed
                # determine filename and optional extra attrs (separated by | and ,)
                filename=tag[1:].strip()
                    
                filename, attrs = self.parseCustomAttrs(filename)
                self.environ["file"]=filename
                mime=mimetypes.guess_type(filename)
                if mime:
                    mime=mime[0] or ""
                stats=self.fileStats(filename)
                if stats:
                    self.environ["sizekb"]=int(math.ceil(stats.st_size / 1024.0))
                    self.environ["short"]=os.path.split(filename)[1]
                    self.environ["icon"]=self.getMimeIcon(mime)
                    if "alt" not in attrs:
                        attrs["alt"] = "[[image: %s]]" % self.environ["short"]
                    self.environ["attrs"]=' '.join( [ '%s="%s"' % (a,v) for a,v in attrs.items() ] )
                    if mime.startswith("image/"):
                        self.parsetree.append( '<img src="%(urlprefix)sfiles/%(userid)s/%(file)s" %(attrs)s />' % self.environ )
                    else:
                        self.parsetree.append( '<a href="%(urlprefix)sfiles/%(userid)s/%(file)s" title="Download file, %(sizekb)d Kb" rel="nofollow"><img alt="download" src="%(urlprefix)simg/%(icon)s" style="padding-bottom:0.5ex" />%(short)s</a>' % self.environ )
                elif filename[:5].lower() == "http:": # external link?
                    scheme,netloc,path,query,fragment = urlparse.urlsplit(filename)
                    self.environ["short"]=os.path.split( path ) [1] or filename
                    self.environ["netloc"]=netloc
                    if mime.startswith("image/"):
                        if "alt" not in attrs:
                            attrs["alt"] = "[[image: %(short)s from %(netloc)s]]" % self.environ
                        self.environ["attrs"]=' '.join( [ '%s="%s"' % (a,v) for a,v in attrs.items() ] )
                        self.parsetree.append( '<img src="%(file)s" %(attrs)s />' % self.environ )
                    else:
                        self.environ["icon"]=self.getMimeIcon(mime)
                        self.parsetree.append( '<a href="%(file)s" title="Download file from %(netloc)s" rel="nofollow"><img alt="remote" src="%(urlprefix)simg/remote.gif" style="padding-bottom:0.5ex" /><img alt="download" src="%(urlprefix)simg/%(icon)s" style="padding-bottom:0.5ex" />%(short)s</a>' % self.environ )
                else:
                    self.parsetree.append( '[[!!! BAD LINK: %(file)s !!!]]' % self.environ)
            elif tag.startswith("url"):
                self.parsetree.append( self.parseURL(tag,extra,matches) )
            elif tag.startswith("img"):
                self.parsetree.append( self.parseIMG(tag, matches) )
            elif tag=="quote":
                self.closeParagraph()
                self.parsetree.append( Quote(self.environ).parse(matches,"/quote") )
                self.openParagraph()
            elif tag=="code":
                self.closeParagraph()
                self.parsetree.append( Code(self.environ).parse(matches,"/code") )
                self.openParagraph()
            elif tag.startswith("list"):
                self.closeParagraph()
                self.parsetree.append( List(extra,self.environ).parse(matches,"/list") )
                self.openParagraph()
            elif tag==closetag:
                break
            else:
                self.processTag(tag, extra, matches)
        self.closeParagraph()            
        if self.closetags!=self.opentags:
            raise MarkupSyntaxError("close tags don't match open tags")

        return self.makeHTML(self.parsetree)

    def parseCustomAttrs(self, txt):
        attrs={}
        values=txt.split('|',1)
        if len(values)==2:
            txt=values[0]
            values=values[1].split(',')
            for v in values:
                if v.startswith("w=") and len(v)>2:
                    attrs["width"]=v[2:]
                elif v.startswith("h=") and len(v)>2:
                    attrs["height"]=v[2:]
                elif v.startswith("alt=") and len(v)>4:
                    attrs["alt"]=v[4:]
                elif v.startswith("float=") and len(v)>6:
                    attrs["style"]="float: "+v[6:]
                else:
                    raise MarkupSyntaxError("invalid attr: "+v)
        return txt,attrs

    def getMimeIcon(self, mime):
        if mime.startswith("image"): return "picture.gif"
        elif mime.startswith("text"): return "text.gif"
        elif mime.startswith("audio"): return "sound.gif"
        elif mime.startswith("video"): return "movie.gif"
        elif mime.startswith("application/x-sh"): return "script.gif"
        else:  return "disk.gif"

    def openParagraph(self, checkFlag=True):
        if not checkFlag or not self.inparagraph:
            self.parsetree.append( "<p>")
            self.inparagraph=True             

    def closeParagraph(self, clearFlag=True):
        if self.inparagraph:
            if self.parsetree[-1]=="<p>":
                del self.parsetree[-1]  # avoid empty paragraphs <p></p>
            else:
                self.parsetree.append("</p>")
            if clearFlag:
                self.inparagraph=False

    def processTag(self, tag, extra, matches):
        self.parsetree.append( '['+cgi.escape(tag)+']' )    # tags must not be processed
        # don't raise an error: raise MarkupSyntaxError("unknown or unmatched tag '%s'" % tag)
    
    def processText(self, txt):
        # don't strip spaces because otherwise certain substrings will be joined together
        txt=cgi.escape(txt)
        txt=self.processSmileys(txt)
        txt=newlineRE.sub('</p>\n<p>', txt)
        if not self.inparagraph:
            self.inparagraph=True
            txt="<p>"+txt
        return txt

    def processSmileys(self,txt):
        if self.environ["smileycolorstr"]:
            # note: the order is important, and also HTML entities should be used.
            txt=txt.replace("&gt;-(", '<img alt="&gt;(" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/evil.gif" />' % self.environ)
            txt=txt.replace("&gt;-)", '<img alt="&gt;)" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/twisted.gif" />' % self.environ)
            txt=txt.replace("(&gt;)", '<img alt="(&gt;)" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/arrow.gif" />' % self.environ)
            txt=txt.replace("(&lt;)", '<img alt="(&lt;)" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/arrowl.gif" />' % self.environ)
            txt=txt.replace("(?)", '<img alt="(?)" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/question.gif" />' % self.environ)
            txt=txt.replace("(!)", '<img alt="(!)" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/exclaim.gif" />' % self.environ)
            txt=txt.replace("(L)", '<img alt="(L)" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/idea.gif" />' % self.environ)
            txt=txt.replace(":-)", '<img alt=":-)" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/smile.gif" />' % self.environ)
            txt=txt.replace(":-D", '<img alt=":-D" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/biggrin.gif" />' % self.environ)
            txt=txt.replace("^_^", '<img alt="^_^" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/cheesygrin.gif" />' % self.environ)
            txt=txt.replace(":-/", '<img alt=":-/" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/sad.gif" />' % self.environ)
            txt=txt.replace(":-((", '<img alt=":((" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/cry.gif" />' % self.environ)
            txt=txt.replace(":-(", '<img alt=":-(" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/frown.gif" />' % self.environ)
            txt=txt.replace(":-S", '<img alt=":-S" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/confused.gif" />' % self.environ)
            txt=txt.replace(";-)", '<img alt=";-)" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/wink.gif" />' % self.environ)
            txt=txt.replace("8-)", '<img alt="8-)" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/cool.gif" />' % self.environ)
            txt=txt.replace(":-P", '<img alt=":-P" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/tongue.gif" />' % self.environ)
            txt=txt.replace("o_o", '<img alt="o_o" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/eek.gif" />' % self.environ)
            txt=txt.replace(":-|", '<img alt=":-|" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/neutral.gif" />' % self.environ)
            txt=txt.replace(":-&gt;", '<img alt=":-&gt;" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/razz.gif" />' % self.environ)
            txt=txt.replace(":-#", '<img alt=":-#" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/redface.gif" />' % self.environ)
            txt=txt.replace("%-|", '<img alt="%%-|" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/rolleyes.gif" />' % self.environ)
            txt=txt.replace(":-O", '<img alt=":-O" class="smiley" src="%(urlprefix)simg/smileys_%(smileycolorstr)s/surprised.gif" />' % self.environ)
        return txt
    
    def makeHTML(self, parsetree):
        return "".join(parsetree)

    def fileStats(self, filename):
        try:
            return os.stat(os.path.join(self.environ["filepath"], filename))
        except OSError:
            return None

    def parseURL(self, tag, href, matches):
        txt, closetag = matches.next().group(1,2)
        if closetag!="/url":
            raise MarkupSyntaxError("url close tag missing")
        if not href:
            href=txt
        prot, ref = urllib.splittype(href)
        if not prot and not ref.startswith('/'):
            prot="http"
            ref="//"+ref
            href="%s:%s" % (prot,ref)
        href, txt = cgi.escape(href.strip()), cgi.escape(txt.strip())
        if self.comment:
            # anti-spam measure; add rel="nofollow" to the link in comments
            # for more info: http://www.google.com/googleblog/2005/01/preventing-comment-spam.html
            return '<a href="%s" rel="nofollow">%s</a>' % (href, txt)
        else:
            return '<a href="%s">%s</a>' % (href,txt)
       
    def parseIMG(self, tag, matches):
        tag, attrs = self.parseCustomAttrs(tag)
        location, closetag = matches.next().group(1,2)
        if closetag!="/img":
            raise MarkupSyntaxError("img close tag missing")
        scheme,netloc,path,query,fragment = urlparse.urlsplit(location)
        short=os.path.split( path ) [1] or filename
        if "alt" not in attrs:
            attrs["alt"] = "[[image %s from %s]]" % (short, netloc)
        attrs=' '.join( [ '%s="%s"' % (a,v) for a,v in attrs.items() ] )
        return '<img src="%s" %s />' % (cgi.escape(location), attrs)


class Quote(Parser):
    def __init__(self, env={}):
        Parser.__init__(self,env)
    def makeHTML(self, parsetree):
        self.closeParagraph()
        return "<blockquote>%s</blockquote>" % "".join(parsetree).strip()

class List(Parser):
    def initialParagraph(self):
        pass  # don't open a paragraph in a code block
    def __init__(self, listtype, env={}):
        Parser.__init__(self,env)
        self.type=listtype
        self.in_listitem=False
    def processTag(self, tag, extra, matches):
        if tag=='*':
            #if self.inparagraph:
            #    raise MarkupSyntaxError("loose text inside a list")
            if self.in_listitem:
                self.parsetree.append("</li>\n")
            self.parsetree.append("<li>")
            self.in_listitem=True
        else:
            Parser.processTag(self, tag, extra, matches)
    def processText(self, txt):
        txt=self.processSmileys(txt)
        if txt.strip():
            return newlineRE.sub('<br />', cgi.escape(txt))
        else:
            return ""
        
    def makeHTML(self, parsetree):
        if self.in_listitem:
            self.parsetree.append("</li>\n")
        if self.type is None:
            otag=ctag="ul"
        elif self.type=='1':
            otag='ol style="list-style-type: decimal;"'
            ctag='ol'
        elif self.type=='a':
            otag='ol style="list-style-type: lower-alpha;"'
            ctag='ol'
        else:
            raise MarkupSyntaxError("invalid list type '%s'" % self.type)
        return "<%s>%s</%s>" % (otag, "".join(parsetree).strip(), ctag)

class Code(Parser):
    def initialParagraph(self):
        pass  # don't open a paragraph in a code block
    def parse(self, matches, closetag="/code"):
        for m in matches:
            txt, tag = m.group(1,2)
            if txt:
                self.parsetree.append( cgi.escape(txt) )
            if tag==closetag:
                break
            else:
                self.parsetree.append( '['+cgi.escape(tag)+']' )    # tags must not be processed
        return self.makeHTML(self.parsetree)
    def makeHTML(self, parsetree):
        return "<pre>%s</pre>" % "".join(parsetree).strip()


# Main entry function:

def content2html(text,env={},comment=False):
    matches=tokenizeRE.finditer(text+"[%s]"%SENTINEL)
    if env["smileys"] is not None:
        env["smileycolorstr"] = ["yellow", "red", "blue"] [env["smileys"]]    # FIXED ORDER
    else:
        env["smileycolorstr"] = None
    parser=Parser(env,comment)
    return parser.parse(matches)


    
def test():
    env={"urlprefix":"/frog/", "userid":"irmen", "filepath":"/home/irmen" }
    #text="[b]b[/b]\n\n[i]i[/i]\n\n[tt]tt[/tt]"
    #text= contentcleanup(text, env )
    #print content2html(text,env)
    text="          gewoon [b]bold[/b] [i]italic[/i] [u]underline[/u] [tt]typewriter[/tt] [b]bold2[/b] gewoon       "
    print "-----"
    text= contentcleanup(text, env )
    print content2html(text,env)

if __name__=="__main__":
    test()

