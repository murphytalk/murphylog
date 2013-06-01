# -*- coding: utf-8 -*-
from myutils import *

import logging
log = logging.getLogger(__name__)

def get_date_from_datetime(dt):
    #logging.info("getting date from :%s",dt)
    return dt[:10]

WEEKDAYS = {
    0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday',
    5:'Saturday', 6:'Sunday'
}

def weekday(dt):
    """
    dt  - DateTime
    返回星期
    """
    return WEEKDAYS[dt.weekday()]

def render_markup_text(text_type):
    """
    格式化文本 => html
    text_type  格式化文本类型
    """
    def markup(text):
        #log.info("rendering structured txt,text type is %s",text_type)
        if text_type == "rs":
            return myRestructuredtext(text)
        elif text_type == "st":
            return structuredtext(text)
        else:
            return BBCode(text)
    return markup


def highlight(keywords):
    """
    highlighting
    """
    def do_highlight(text):
        #log.debug("highlighting keywords [%s]",keywords)
        if keywords is not None:
            regex=re.compile('('+keywords+')',re.I)#case insensitive
            found=regex.search(text)
            if found:
                text = regex.sub('<span class="highlight">'+found.groups(0)[0]+'</span>',text)
        return text

    return do_highlight
