# -*- coding:utf-8 -*-
import re

def normalize_title(title):
    '''
    Casts strings to a representation suitable for searching
    stripping out details insignificant for comparision.
    '''
    title=re.sub(re.compile(r'\+'),'_plus_',title)
    title=re.sub(re.compile(r'[&\,\.\(\)\-\!\'\"\`\?\_\:\;\$\]\[\#\/]'),'_',title)
    title=re.sub(re.compile(r'\s+'),'',title)
    return (title or safe_title).encode('UTF-8')
