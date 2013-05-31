#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
defined a new directive: sh and a new writer： myhtml

"""

#========================================================================================
# Directive Type:	"sh" (SyntaxHighlighting)
# Doctree Element:	literal_block
# Directive Arguments:	one
# Directive Options:	None.
# Directive Content:	create a literal_block with option : {"syntax":"language"}
from docutils import nodes
from docutils.parsers.rst import directives

def syntax_highlighting(name, arguments, options, content, lineno,
                        content_offset, block_text, state, state_machine):
    if not content:
        warning = state_machine.reporter.warning(
            'Content expected for the "%s" directive; none found.'
            % name, nodes.literal_block(block_text, block_text), line=lineno)
        return [warning]
    text = '\n'.join(content)
    node = nodes.literal_block(text, text)

    node.option = {"syntax":arguments[0]} #check if this option is availble to distinguish with
                                          #normal literal block directive

    node.line = content_offset + 1
    return [node]

#parsed_literal.options = {'class': directives.class_option}
syntax_highlighting.content = True         #we have content
syntax_highlighting.arguments = (1, 0, 1)  #(required_arguments,optional_arguments,final_argument_whitespace)

#register the new directive
directives.register_directive("sh",syntax_highlighting)
#========================================================================================

#========================================================================================
# new writer: inherited from html4css1
# it recognize output of the new directive: sh
from docutils.writers.html4css1 import Writer,HTMLTranslator
from docutils import writers

class MyHtmlWriter(Writer):
    def __init__(self):
        writers.Writer.__init__(self)
        #super(MyHtmlWriter,self).__init__(self)
        self.translator_class = MyHTMLTranslator

class MyHTMLTranslator(HTMLTranslator):
    def visit_literal_block(self, node):
        if hasattr(node,'option') and node.option.has_key('syntax'):
            self.body.append(self.starttag(node, 'pre', CLASS="brush: %s"%node.option['syntax']))
        else:
            HTMLTranslator.visit_literal_block(self,node)

import docutils.writers

#patch the "writer register"
original_get_writer_class = docutils.writers.get_writer_class

def patched_get_writer_class(writer_name):
    if writer_name == "myhtml":
        return MyHtmlWriter
    else:
        return original_get_writer_class(writer_name)

docutils.writers.get_writer_class = patched_get_writer_class
#========================================================================================

if __name__ == "__main__":
    src="""
my docutils enhancement.

normal literal block::

 i am literal block

END of literal block.

html raw:

.. raw:: html

 <font size=1>test</font>

END of raw

syntax highlight:

.. sh:: cpp

   void CController::call(int idx,BASES& objs)
   {
       for(BASES::iterator pos=objs.begin();pos!=objs.end();++pos){
           ((*pos)->*(m_funcs[idx-1]))();
       }
   }


END of syntax highlight
    """
    from docutils.core import publish_parts

    parts = publish_parts(source=src, writer_name="myhtml",settings_overrides={'raw_enabled':False})
    print parts["fragment"]
