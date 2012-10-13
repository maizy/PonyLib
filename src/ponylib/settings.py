# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2011-2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

# -------------------------------------------
#
# Normally you shouldn't edit those settings
# directly.
#
# See settings/settings.json
#
# -------------------------------------------



import sys
import os.path as path

# -------------------------------------------
# Ponylib settings

PROJECT_ROOT = path.realpath(path.join(path.dirname(__file__), '..', '..'))
WEB_ROOT = path.join(PROJECT_ROOT, 'src', 'ponylib')
VAR_ROOT = path.join(PROJECT_ROOT, 'var')
BIN_ROOT = path.join(PROJECT_ROOT, 'src', 'tools')
LIB_ROOT = path.join(PROJECT_ROOT, 'src')

#libs
if LIB_ROOT not in sys.path:
    sys.path.append(LIB_ROOT)


# -------------------------------------------
# Text search engine settings

PONYLIB_TEXT_SEARCH_ENGINE = None
PONYLIB_TEXT_SEARCH_ENGINE_OPTS = {}


# -------------------------------------------
# wine settings
#WINEBIN_ROOT = path.join(PROJECT_ROOT, 'wine_bin')
##fb2lrf
#PONYLIB_BIN_FB2LRF = path.join(WINEBIN_ROOT, 'fb2lrf_console', 'fb2lrf_c.exe')
#PONYLIB_BIN_FB2LRF_USE_WINE = (platform.system() != 'Window') #Set False on Windows
#
##wine
#PONYLIB_BIN_WINE = '/usr/bin/env wine'


# -------------------------------------------
# Lang & locale

USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'


# -------------------------------------------
# Django settings

AUTOLOAD_SITECONF = 'ponylib.on_load'
ROOT_URLCONF = 'ponylib.urls'

INSTALLED_APPS = (
    'autoload',
    'ponylib',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'south',
)

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

SITE_ID = 1

MEDIA_ROOT = path.join(VAR_ROOT, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = path.join(VAR_ROOT, 'static-deploy')
STATIC_URL = '/static/'

STATIC_KEY = '002'

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    path.join(WEB_ROOT, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = 'ponyponymagicpony'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',

    'ponylib.utils.context_processors.static_key.static_key'
)

MIDDLEWARE_CLASSES = (
    'autoload.middleware.AutoloadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
)



TEMPLATE_DIRS = ()


# -------------------------------------------
# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


# ------------------------------------------
# Test settings

SKIP_SOUTH_TESTS = True

NO_DB_TESTS = False

# -------------------------------------------
# Debug

DEBUG = False
TEMPLATE_DEBUG = False
DEBUG_TOOLBAR = False

# -------------------------------------------
# Database
DATABASES = {
    'default': {
        # 'postgresql_psycopg2', 'mysql', 'sqlite3'
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ponylib',
        'USER': 'ponylib',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# -------------------------------------------
# Overwrite settings from settings/settings.json
# TODO: do it less hacky
PONYLIB_JSON_SETTINGS_PATH = path.join(PROJECT_ROOT, 'settings', 'settings.json')
from ponylib.utils import json_settings
json_settings.settings_path = PONYLIB_JSON_SETTINGS_PATH
from ponylib.utils.json_settings.export import *

# -------------------------------------------
# Debug 2
TEMPLATE_DEBUG = DEBUG

if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware', )
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar', 'bshell', )
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
        'INTERCEPT_REDIRECTS': False,
    }
