# -*- coding: utf-8 -*-
# $Id$
import datetime

# blog models
from django     import forms
from django.db  import models
import django.contrib.auth
# --- from tags app ---
import murphytalk_django.tags.models
import murphytalk_django.tags.fields

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
    class EntryChangeManipulator(models.manipulators.AutomaticChangeManipulator):
        def __init__(self,obj,follow=None):
            #super(EntryChangeManipulator, self).__init__(obj,follow)
            models.manipulators.AutomaticChangeManipulator.__init__(self,obj,follow)
            self.fields = (
                #forms.TextField(field_name="title",maxlength=200,length=80,is_required=True),
                forms.LargeTextField(field_name="title",cols=80,rows=1, is_required=True),
                forms.LargeTextField(field_name="subject",cols=80,rows=15, is_required=True),
                forms.LargeTextField(field_name="text", cols=80,rows=25,is_required=False),
                forms.CheckboxField(field_name="private"),
                forms.SelectField(field_name="text_type",choices=Entry.TEXT_TYPE_CHOICES),
                murphytalk_django.tags.fields.TagsFormField('tags',50),
            )

        def save(self,new_data):
            self.original_object.last_edit=datetime.datetime.now()
            #return super(Entry.EntryChangeManipulator, self).save(new_data)
            return models.manipulators.AutomaticChangeManipulator.save(self,new_data)


    class EntryAddManipulator(models.manipulators.AutomaticAddManipulator):
        def __init__(self,follow=None):
            #models.manipulators.AutomaticAddManipulator.__init__(self,follow)
            self.follow = self.opts.get_follow(follow)
            self.fields = (
                forms.LargeTextField(field_name="title",cols=80,rows=1, is_required=True),
                forms.LargeTextField(field_name="subject",cols=80,rows=15, is_required=True),
                forms.LargeTextField(field_name="text", cols=80,rows=25,is_required=False),
                forms.CheckboxField(field_name="private"),
                forms.SelectField(field_name="text_type",choices=Entry.TEXT_TYPE_CHOICES),
                murphytalk_django.tags.fields.TagsFormField('tags',50),
            )


    TEXT_TYPE_CHOICES = (
        ('rs','reStructured Text'),
        ('st','Structured Text'),
        ('bb','BB Code'),
    )


#    def __init__(self, *args, **kwargs):
#        models.Model.__init__(self, *args, **kwargs)
#        self.ChangeManipulator = Entry.EntryChangeManipulator

    #owner user
    owner    = models.ForeignKey(django.contrib.auth.models.User)
    owner.get_default=get_me #取得默认值。manipulator会调用此函数获得默认值。此处返回在view中设置好的当前user

    #title
    title    = models.CharField('Title',maxlength=200)

    #date posted(includes time)
    post_date = models.DateTimeField('Date Posted')
    post_date.get_default = lambda : datetime.datetime.now() #取得默认值。供new manipulator用

    #subject
    subject  = models.TextField('Subject')

    #text
    text     = models.TextField('Text',null=True)

    #text type
    text_type= models.CharField(maxlength=2,choices=TEXT_TYPE_CHOICES)

    #time of last edit
    last_edit= models.DateTimeField('Date of last edit')
    last_edit.get_default = lambda : datetime.datetime.now() #取得默认值。供new manipulator用

    #private
    #users other than the owner will not see this post
    private  = models.BooleanField('Private')

    #tags
    tags = murphytalk_django.tags.fields.TagsField(murphytalk_django.tags.models.Tag)

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

    def __str__(self):
        return self.title+'@'+str(self.post_date)

    class Admin:
        pass
