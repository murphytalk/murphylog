# -*- coding: utf-8 -*-
# Django settings for murphytalk_django project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

LINUX = True

ADMINS = (
    ('murphytalk', 'murphytalk@gmail.com'),
)

MANAGERS = ADMINS

if LINUX:
    # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
    DATABASE_ENGINE = 'mysql'
    DATABASE_NAME   = 'django_db'
else:
    DATABASE_ENGINE = 'sqlite3'
    DATABASE_NAME = 'C:/LM/Projects/extra/Django/murphytalk_django/my_django_site/murphytalk_django.db3'

#try to load template dir from envrion var
MY_TEMPLATE_DIR = os.environ.get('DJANGO_TEMPLATE_DIR')
if MY_TEMPLATE_DIR is None:
    MY_TEMPLATE_DIR="/home/murphy/work/django/HOMEPAGE/murphytalk_django/my_django_site/template"


DATABASE_USER = 'root'             # Not used with sqlite3.
DATABASE_PASSWORD = 'java2'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'Asia/Tokyo'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '7&acgu_(yr*_wh&sfy0g)f-!2j+m0rxhr285m-c5hdkz=@t%w5'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    #'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    'django.middleware.locale.LocaleMiddleware',
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.doc.XViewMiddleware",
)

ROOT_URLCONF = 'murphytalk_django.urls'

if LINUX:
    TEMPLATE_DIRS = (
        # Put strings here, like "/home/html/django_templates".
        # Always use forward slashes, even on Windows.
        MY_TEMPLATE_DIR,
    )
else:
    TEMPLATE_DIRS = (
        "C:/LM/Projects/extra/Django/murphytalk_django/my_django_site/template",
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'murphytalk_django.murphymarkup',
    'murphytalk_django.murphylog',
    'murphytalk_django.tagsfield',

    'django.contrib.comments', #因为murphylog重载了Comments的模板所以得把comments排在murphylog后面
                               #以保证被找到的不是comments模板
    )

#-------------------------------------------------
#自定义设置
#-------------------------------------------------

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "murphytalk_django.murphylog.utils.free_comment_context_processor",
    )

#tags app的路径设置
STYLE_URL = "/media/tags/"
JS_URL    = "/media/tags/"


RESTRUCTUREDTEXT_FILTER_SETTINGS={'file_insertion_enabled': 0,
                                  'raw_enabled': 0,
                                  '_disable_config': 1}
