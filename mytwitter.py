# -*- coding: utf-8 -*-
# coding=utf-8

CONSUMER_KEY = '2wuTKus9SVUm2SgpYxJcQ'
CONSUMER_SECRET = 'TxeZ2Zrtvpyfs9QHLj9f7IkniwFPUIJ90gQ3FJH1g'
OAUTH_FILENAME = 'auth_token.txt'

from twitter.api import Twitter, TwitterError
from twitter.oauth import OAuth, write_token_file, read_token_file
from twitter.oauth_dance import oauth_dance

import sys

sys.path.insert(0, 'lib/twitter.zip')

import logging

#from blog import MyRequestHandler

#class MyTweets(MyRequestHandler):
#    def get(self):

def get_twitter(need_auth=False):
    if need_auth:
        oauth_token, oauth_token_secret = read_token_file(OAUTH_FILENAME)
        auth = OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET)
    else:
        auth = None

    twitter = Twitter(
        auth=auth,
        secure=True,
        api_version='1',
        domain='api.twitter.com')

    return twitter


def get_my_tweets():
    twitter = get_twitter()
    tweets = twitter.statuses.user_timeline(user_id="murpytalk", count=5)
    for t in tweets:
        logging.info(t)


def get_my_twitter_profile():
    twitter = get_twitter()
    return twitter.users.show(id="murphytalk")


def auth():
    oauth_dance(
        "murphytalk", CONSUMER_KEY, CONSUMER_SECRET,
        OAUTH_FILENAME)


if __name__ == '__main__':
    #auth()
    get_my_tweets()
