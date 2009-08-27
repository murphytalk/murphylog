# -*- coding: utf-8 -*-
# $Id$
import datetime

# blog models
from django     import forms
from django.db  import models
import django.contrib.auth

# --- from tagsfield app ---
from tagsfield.models import Tag
from tagsfield import fields

#will be set to current user in view
me=None

def get_me():
    """
    return current user's id
    """
    global me
    if me is None:
        return None
    else:
        return me.id


class Entry(models.Model):
    TEXT_TYPE_CHOICES = (
        (u'rs',u'reStructured Text'),
        (u'st',u'Structured Text'),
        (u'bb',u'BB Code'),
    )


#    def __init__(self, *args, **kwargs):
#        models.Model.__init__(self, *args, **kwargs)
#        self.ChangeManipulator = Entry.EntryChangeManipulator

    #owner user
    owner    = models.ForeignKey(django.contrib.auth.models.User)
    owner.default=get_me #取得默认值。此处返回在view中设置好的当前user

    #title
    title    = models.CharField('Title',max_length=200)

    #date posted(includes time)
    post_date = models.DateTimeField('Date Posted')
    post_date.default = lambda : datetime.datetime.now() #取得默认值

    #subject
    subject  = models.TextField('Subject')

    #text
    text     = models.TextField('Text',null=True)

    #text type
    text_type= models.CharField(max_length=2,choices=TEXT_TYPE_CHOICES)

    #time of last edit
    last_edit= models.DateTimeField('Date of last edit')
    last_edit.default = lambda : datetime.datetime.now() #取得默认值

    #private
    #users other than the owner will not see this post
    private  = models.BooleanField('Private')

    #tags
    tags = fields.TagsField(Tag)

    def getTags(self):
        """
        return related tags in a list for using in template
        [[tag1's id,tag1's value,tag1's tag_note],]
        """
        local_tags=[]
        for tag in self.tags.all():
            local_tags.append([tag.id,tag.value,tag.tag_note])
        return local_tags

    def ifCanShowEntry(self):
        """
        return True is this entry belongs to user
        """
        return (user.id == self.owner.id) or not self.private

    def __unicode__(self):
        return self.title+u'@'+unicode(self.post_date)

    class Admin:
        pass
