#######################################################
# Copyright: ZopeChina Corp, Ltd. http://zopechina.com
#######################################################

from StructuredText.DocumentClass import StructuredTextEmphasis, StructuredTextStrong, StructuredTextUnderline, DocumentClass, StructuredTextLiteral

import re
from string import split, join, replace, expandtabs, strip, find, rstrip
from StructuredText.STletters import letters, digits, literal_punc, under_punc,\
     strongem_punc, phrase_delimiters,dbl_quoted_punc

# HighLight the ' ' words
def doc_literal(
        self, s,
        # patch for chinese
        #expr = re.compile(r"(\W+|^)'([%s%s%s\s]+)'([%s]+|$)" % (letters, digits, literal_punc, phrase_delimiters)).search,):
        expr = re.compile(r"(\W+|^)'([^']+)'(\W+|$)").search,):

        r=expr(s) #or expr2(s)
        if r:
            start, end = r.span(2)
            return (StructuredTextLiteral(s[start:end]), start-1, end+1)
        else:
            return None

def doc_emphasize(
        self, s,
        expr = re.compile(r'\*([^\*]+?)\*').search
        ):

        r=expr(s)
        if r:
            start, end = r.span(1)
            return (StructuredTextEmphasis(s[start:end]), start-1, end+1)
        else:
            return None

def doc_underline(self,
                      s,
                      expr=re.compile(r'_([^_]+)_([\s%s]|$)' % (phrase_delimiters)).search):

        result = expr(s)
        if result:
            if result.group(1)[:1] == '_':
               return None # no double unders
            start,end = result.span(1)
            st,e = result.span()
            return (StructuredTextUnderline(s[start:end]),st,e-len(result.group(2)))
        else:
            return None

def doc_strong(self,
                   s,
                   expr = re.compile(r'\*\*([^\*]+?)\*\*').search
        ):

        r=expr(s)
        if r:
           start, end = r.span(1)
           return (StructuredTextStrong(s[start:end]), start-2, end+2)
        else:
           return None

_DQUOTEDTEXT1 = r'("[^\"]+")'
_ABSOLUTE_URL=r'((http|https|ftp|mailto|file|about)[:/]+?[%s0-9_\@\.\,\?\!\/\:\;\-\#\~\=\&\%%\+]+)' % letters
_ABS_AND_RELATIVE_URL=r'([%s0-9_\@\.\,\?\!\/\:\;\-\#\~\=\&\%%\+]+)' % letters
_SPACES = r'(\s*)'

def doc_href1(self, s,
                  expr=re.compile(_DQUOTEDTEXT1 + "(:)" + _ABS_AND_RELATIVE_URL + _SPACES).search
                   ):
        return self.doc_href(s, expr)

def doc_href2(self, s,
                  expr=re.compile(_DQUOTEDTEXT1 + r'(\,\s+)' + _ABSOLUTE_URL + _SPACES).search
                   ):
        return self.doc_href(s, expr)

DocumentClass.doc_href1 = doc_href1
DocumentClass.doc_href2 = doc_href2
DocumentClass.doc_literal = doc_literal
DocumentClass.doc_emphasize = doc_emphasize
DocumentClass.doc_strong = doc_strong
DocumentClass.doc_underline = doc_underline
