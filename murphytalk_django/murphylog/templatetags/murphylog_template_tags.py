# -*- coding: utf-8 -*-
from django.template import Node, NodeList, resolve_variable
from django.template import VariableDoesNotExist
from django.template import Library

register = Library()


class IfShowPrivateNode(Node):
    def __init__(self, entry, user, nodelist_true, nodelist_false, negate):
        self.entry, self.user = entry, user
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.negate = negate

    def __repr__(self):
        return "<IfShowPrivateNode>"

    def render(self, context):        
        try:
            private = resolve_variable("%s.private"%self.entry, context)
        except VariableDoesNotExist:
            private = None
            
        try:
            ownerid = resolve_variable("%s.owner.id"%self.entry, context)
        except VariableDoesNotExist:
            ownerid = None
            
        try:
            userid = resolve_variable("%s.id"%self.user, context)
        except VariableDoesNotExist:
            userid = None #for anonymous user userid would be None

        if private and ownerid and (userid is None or userid != ownerid):
            return self.nodelist_false.render(context)
        else:
            return self.nodelist_true.render(context)


def do_if_show_private(parser, token, negate):
    """
    接受两个参数：entry user

    如果entry.private==False或者entry.owner==user则返回if部分
    否则返回else部分

    Examples::

        {% if_show_private entry user %}
            ...
        {% else %}
            ...
        {% endifshowprivate %}
    """
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes two arguments" % bits[0]
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfShowPrivateNode(bits[1], bits[2], nodelist_true, nodelist_false, negate)

#@register.tag
def if_show_private(parser, token):
    return do_if_show_private(parser, token, False)
if_show_private = register.tag(if_show_private)

#替换Sunday,YYYY-MM-DD为Sunday<BR>YYYY-MM-DD
def break_weekday(value):
    return value.replace(",","<BR>")
    
register.filter(break_weekday)
