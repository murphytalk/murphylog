# -*- coding: utf-8 -*-
# $Id$
import cgi

import django.contrib.auth
import django.http

from django.shortcuts                   import render_to_response

from django.views.generic.list_detail   import object_list
from django.views.generic.list_detail   import object_detail
from django.views.generic.create_update import update_object
from django.views.generic.create_update import create_object
from django.views.generic.create_update import delete_object

from django.db.models import Q

from django import forms

# --- from free comments app ---
#from django.contrib.comments.views.comments import post_free_comment as django_post_free_comment
#from django.contrib.comments.models import FreeComment

# --- from tags app ---
from murphytalk_django.tagsfield.models      import Tag

# --- from this app ---
from murphytalk_django.murphylog.models import Entry

import murphytalk_django.murphylog.models

class EntryPostForm(forms.ModelForm):
    #title
    title   = forms.CharField(widget=forms.widgets.Textarea(attrs = {'cols': '80', 'rows': '1'}),max_length=200)
    #subject
    subject = forms.CharField(widget=forms.widgets.Textarea(attrs = {'cols': '80', 'rows': '15'}),max_length=200)
    #text
    text    = forms.CharField(widget=forms.widgets.Textarea(attrs = {'cols': '80', 'rows': '25'}),required=False)
    #private
    private = forms.BooleanField(required=False)

    class Meta:
        model = Entry


# max posts displayed in one page
POSTS_PER_PAGE = 10

#return basic context dict
def get_basic_context(tag_id=None):
    #build tag cloud
    def update_tag_list():
        sumv = 0
        tags = Tag.objects.all()

        local_tag_list = []

        for t in tags:
            entries= Entry.objects.filter(tags=t.id)
            count = entries.count()
            if count>0:
                local_tag_list.append([t.id,t.value,t.tag_note,count])
                sumv = sumv + count

        #average posts
        tags_count=tags.count()
        if tags_count > 0 and sumv> tags_count:
            avg = sumv / tags_count
        else:
            avg = 1

        #set font size
        for t in local_tag_list:
            font_size = 100*t[3]/avg
            if font_size >200:
                font_size = 200
            elif font_size < 90:
                font_size = 90

            t.append(font_size) #t[4]

        return local_tag_list

    #tag cloud
    tag_list=update_tag_list()

    #recent comments
    comments=None#FreeComment.objects.all().order_by("-id")[:5]

    my_extra_context={"tag_list"         :tag_list,                   #tag cloud,
                      "total_posts_num"  :Entry.objects.all().count(),#number of total posts
                      "comments"         :comments,
                      "highlight_keyword":None,
                      }


    if tag_id:
        tagid=int(tag_id)
        #called by tagged page,get tag info
        for t in tag_list:
            #look for tag by tag id
            if t[0]==tagid:
                my_extra_context["tag_id"]  =t[0]
                my_extra_context["tag_name"]=t[1]
                my_extra_context["tag_note"]=t[2]
                break

    return my_extra_context


def do_index(request,entries,page_num=None,tag_id=None):
    """
    render entry lists page
    case 1: default index page
    case 2: index page with sepcified page number
    case 3: entry lists with specified one tag
    case 4: entry lists with specified one tag and page number
    """
    #posts number of current tag
    tag_total_posts_num = entries.count()

    pages = tag_total_posts_num/POSTS_PER_PAGE

    if (tag_total_posts_num%POSTS_PER_PAGE)>0:
        pages=pages+1

    #extra context passed to template
    my_extra_context = get_basic_context(tag_id)
    my_extra_context["page_range"]=range(1,pages+1) #page range
    my_extra_context["user"]      =request.user     #user object

    if tag_id is None:
        templateName="blog/index.djhtml"
    else:
        templateName="blog/taggedIndex.djhtml"

    return object_list(request,
                       entries,
                       page          = page_num,
                       paginate_by   = POSTS_PER_PAGE,
                       template_name = templateName,
                       allow_empty   = True,
                       extra_context = my_extra_context,
                       template_object_name = "entry")

# default index page (with or whitout page)
def index(request,page=None):
    """
    URL:  /blog/
          /blog/page/<page number>
          the main index page
    """
    #sort all entries by id
    all_entries = Entry.objects.order_by('-id')
    return do_index(request,all_entries,page_num=page)

# single detailed entry
def detail(request,eid,highlightWord=None):
    """
    URL: /blog/<entry id>
    """
    total_posts_num = Entry.objects.all().count()

    entry=Entry.objects.filter(id=eid)

    if not request.user.is_authenticated() and entry[0].private:
        return django.http.HttpResponsePermanentRedirect('/blog/')

    my_extra_context = get_basic_context()
    my_extra_context["show_detail"]=True
    my_extra_context["highlight_keyword" ]=highlightWord

    return object_detail(request,Entry.objects.all(),object_id=eid,
                         template_name='blog/detail.djhtml',
                         extra_context=my_extra_context,
                         template_object_name='entry')

def postedDetail(request,eid):
    """
    the detailed page after a successful post
    """
    return detail(request,eid)

# index page of specified tag
def taggedIndex(request,tag_id,page=None):
    """
    URL: /blog/tag/<tag id>
         /blog/tag/page/<tag id>
    """
    entries = Entry.objects.filter(tags=tag_id).order_by('-id')
    return do_index(request,entries,page_num=page,tag_id=tag_id)


def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = django.contrib.auth.authenticate(username=username, password=password)
    if user is not None:
        #login the user
        django.contrib.auth.login(request, user)
    return django.http.HttpResponsePermanentRedirect('/blog/')

def logout(request):
    django.contrib.auth.logout(request)
    return django.http.HttpResponsePermanentRedirect('/blog/')

# edit an entry
def update(request,eid):
    """
    edit a post
    URL: /blog/edit/<entry id>
    """
    if request.user.id != Entry.objects.get(id=eid).owner.id:
        return django.http.HttpResponsePermanentRedirect('/blog/')

    #remember current user
    murphytalk_django.murphylog.models.me = request.user

    if request.POST.has_key("delete"):
        if FreeComment.objects.filter(object_id=int(eid)).count()==0:
            #delete object
            result = delete_object(request,Entry,object_id=eid,
                                   post_delete_redirect="/blog/")
        else:
            #this post has comments,cannot be deleted
            return django.http.HttpResponsePermanentRedirect('/blog/')
    else:
        my_extra_context = get_basic_context()
        my_extra_context["update_post"]=True
        #passin count of comments,only display delete button for posts with 0 comment
        #my_extra_context["comment_count"]=FreeComment.objects.filter(object_id=int(eid)).count()

        result = update_object(request,Entry,object_id=eid,
                               form_class = EntryPostForm,
                               login_required=True,
                               post_save_redirect="/blog/entryposted/%(id)s/",#goto posted detail page after posted
                               template_name="blog/update_entry.djhtml",
                               extra_context=my_extra_context)
#                               follow={"post_date":False,"last_edit":False})


    return result

# create a new entry
def new(request):
    """
    new post
    URL: /blog/new/
    """
    if not request.user.is_authenticated():
        return django.http.HttpResponsePermanentRedirect('/blog/')

    #remember current user
    murphytalk_django.murphylog.models.me = request.user

    my_extra_context = get_basic_context()

    result = create_object(request,Entry,
                           login_required=True,
                           post_save_redirect="/blog/entryposted/%(id)s/",#goto posted detail page after posted
                           template_name="blog/update_entry.djhtml",
                           extra_context=my_extra_context)


    return result

# free comment page
def post_free_comment(request):
    """
    URL: /blog/postfreecomment/
    """
    #add extra context to reqeust object
    request.META["murphylog_context"]=get_basic_context()
    return django_post_free_comment(request)

# after free comment is submitted
def commentPosted(request):
    c=request.GET.get('c',None) #c -> content id:object id
    if c is None:
        return django.http.HttpResponsePermanentRedirect('/blog/')
    else:
        cid,eid=c.split(':')
        return postedDetail(request,eid)


#search
def search(request,searchFor=None):
    """
    URL: /blog/search/searchfor/
    """
    urlcmd='p='+searchFor
    searchFor=cgi.parse_qs(urlcmd)['p'][0]
    entries = Entry.objects.filter(Q(title__icontains=searchFor)|Q(subject__icontains=searchFor)|Q(text__icontains=searchFor)).order_by("-id")
    return render_to_response('blog/search_result.djhtml',{"keyword":searchFor,"entries":entries})
