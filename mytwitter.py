# -*- coding: utf-8 -*-
# coding=utf-8

CONSUMER_KEY   ='2wuTKus9SVUm2SgpYxJcQ'
CONSUMER_SECRET='TxeZ2Zrtvpyfs9QHLj9f7IkniwFPUIJ90gQ3FJH1g'
OAUTH_FILENAME ='auth_token.txt'

from twitter.api import Twitter, TwitterError
from twitter.oauth import OAuth, write_token_file, read_token_file
from twitter.oauth_dance import oauth_dance

import sys
sys.path.insert(0, 'lib/twitter.zip')

import logging

#from blog import MyRequestHandler

#class MyTweets(MyRequestHandler):
#    def get(self):

def get_my_tweets():
    oauth_token, oauth_token_secret = read_token_file(OAUTH_FILENAME)

    twitter = Twitter(
        auth=OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET),
        secure=True,
        api_version='1',
        domain='api.twitter.com')

    tweets = twitter.statuses.user_timeline()
    for t in tweets:
        #print t["text"]
        logging.info(t["text"])


def auth():
    oauth_dance(
        "murphytalk", CONSUMER_KEY, CONSUMER_SECRET,
        OAUTH_FILENAME)


if __name__ == '__main__':
    #auth()
    get_my_tweets()
