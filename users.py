__author__ = 'murphy'

import logging

USERFILE = "users.txt"
valid_users = set()

def load_users(user_fname):
    global USERFILE
    global valid_users
    emails = open(USERFILE).readlines()
    for e in emails:
        if e[0]=='#':
            continue
        if e[-1]=='\n' or e[-1]=='\r':
            e = e[0:-1]
            valid_users.add(e)

def is_valid_user(user):
    global valid_users
    return user.email() in valid_users

#GAE will cache the imported modules,so we are loading the file only once
#logging.info("loading user emails from %s"%USERFILE)
load_users(USERFILE)
