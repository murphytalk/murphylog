def processSmileys(txt):
    # note: the order is important, and also HTML entities should be used.
    txt=txt.replace("&gt;-(", '<img alt="&gt;(" class="smiley" src="/media/blog/img/smileys_yellow/evil.gif" />' )
    txt=txt.replace("&gt;-)", '<img alt="&gt;)" class="smiley" src="/media/blog/img/smileys_yellow/twisted.gif" />' )
    txt=txt.replace("(&gt;)", '<img alt="(&gt;)" class="smiley" src="/media/blog/img/smileys_yellow/arrow.gif" />' )
    txt=txt.replace("(&lt;)", '<img alt="(&lt;)" class="smiley" src="/media/blog/img/smileys_yellow/arrowl.gif" />' )
    txt=txt.replace("(?)", '<img alt="(?)" class="smiley" src="/media/blog/img/smileys_yellow/question.gif" />' )
    txt=txt.replace("(!)", '<img alt="(!)" class="smiley" src="/media/blog/img/smileys_yellow/exclaim.gif" />' )
    txt=txt.replace("(L)", '<img alt="(L)" class="smiley" src="/media/blog/img/smileys_yellow/idea.gif" />' )
    txt=txt.replace(":-)", '<img alt=":-)" class="smiley" src="/media/blog/img/smileys_yellow/smile.gif" />' )
    txt=txt.replace(":)", '<img alt=":-)" class="smiley" src="/media/blog/img/smileys_yellow/smile.gif" />' )
    txt=txt.replace(":-D", '<img alt=":-D" class="smiley" src="/media/blog/img/smileys_yellow/biggrin.gif" />' )
    txt=txt.replace("^_^", '<img alt="^_^" class="smiley" src="/media/blog/img/smileys_yellow/cheesygrin.gif" />' )
    txt=txt.replace(":-/", '<img alt=":-/" class="smiley" src="/media/blog/img/smileys_yellow/sad.gif" />' )
    txt=txt.replace(":-((", '<img alt=":((" class="smiley" src="/media/blog/img/smileys_yellow/cry.gif" />' )
    txt=txt.replace(":-(", '<img alt=":-(" class="smiley" src="/media/blog/img/smileys_yellow/frown.gif" />' )
    txt=txt.replace(":(" , '<img alt=":-(" class="smiley" src="/media/blog/img/smileys_yellow/frown.gif" />' )
    txt=txt.replace(":-S", '<img alt=":-S" class="smiley" src="/media/blog/img/smileys_yellow/confused.gif" />' )
    txt=txt.replace(";-)", '<img alt=";-)" class="smiley" src="/media/blog/img/smileys_yellow/wink.gif" />' )
    txt=txt.replace(";)", '<img alt=";-)" class="smiley" src="/media/blog/img/smileys_yellow/wink.gif" />' )
    txt=txt.replace("8-)", '<img alt="8-)" class="smiley" src="/media/blog/img/smileys_yellow/cool.gif" />' )
    txt=txt.replace(":-P", '<img alt=":-P" class="smiley" src="/media/blog/img/smileys_yellow/tongue.gif" />' )
    txt=txt.replace("o_o", '<img alt="o_o" class="smiley" src="/media/blog/img/smileys_yellow/eek.gif" />' )
    txt=txt.replace(":-|", '<img alt=":-|" class="smiley" src="/media/blog/img/smileys_yellow/neutral.gif" />' )
    txt=txt.replace(":-&gt;", '<img alt=":-&gt;" class="smiley" src="/media/blog/img/smileys_yellow/razz.gif" />' )
    txt=txt.replace(":-#", '<img alt=":-#" class="smiley" src="/media/blog/img/smileys_yellow/redface.gif" />' )
    txt=txt.replace("%-|", '<img alt="%%-|" class="smiley" src="/media/blog/img/smileys_yellow/rolleyes.gif" />' )
    txt=txt.replace(":-O", '<img alt=":-O" class="smiley" src="/media/blog/img/smileys_yellow/surprised.gif" />' )
    return txt
    
