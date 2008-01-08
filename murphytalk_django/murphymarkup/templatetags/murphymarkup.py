"""
my own markup tags
"""
import re

from django import template
from django.conf import settings

from murphytalk_django.murphymarkup.templatetags.TextType.stx import stx2html
from murphytalk_django.murphymarkup.templatetags.BBCode.default import content2html
from murphytalk_django.murphymarkup.templatetags.utils import processSmileys

register = template.Library()

#reStructuredText with smileyfaces
#refer to django's contrib/markup
def myRestructuredtext(value):
    try:
        from docutils.core import publish_parts
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError, "Error in {% restructuredtext %} filter: The Python docutils library isn't installed."
        return value
    else:
        docutils_settings = getattr(settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {})
        parts = publish_parts(source=value, writer_name="html4css1", settings_overrides=docutils_settings)
        return processSmileys(parts["fragment"])

register.filter(myRestructuredtext)


#Structured Text
def structuredtext(value):
    try:
        html=processSmileys(stx2html(value))
    except:
        return value
    else:
        return html

register.filter(structuredtext)

#BBCode from snakelet/frog
def BBCode(value):
    try:
        html=content2html(value)
    except:
        return value
    else:
        return html

register.filter(BBCode)


#highlighting
def highlight(html,keywords):
    if keywords is not None:
        regex=re.compile('('+keywords+')',re.I)#case insensitive
        found=regex.search(html)
        if found:
            html = regex.sub('<span class="highlight">'+found.groups(0)[0]+'</span>',html)

    return html

register.filter(highlight)
