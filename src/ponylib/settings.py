# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2011-2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""


import sys
import os.path as path
import platform
import importlib


# Ponylib settings

PROJECT_ROOT = path.realpath(path.join(path.dirname(__file__), '..', '..'))

WEB_ROOT = path.join(PROJECT_ROOT, 'src', 'ponylib')

VAR_ROOT = path.join(PROJECT_ROOT, 'var')

BIN_ROOT = path.join(PROJECT_ROOT, 'bin')

WINEBIN_ROOT = path.join(PROJECT_ROOT, 'wine_bin')

LIB_ROOT = path.join(PROJECT_ROOT, 'src')

#libs
if LIB_ROOT not in sys.path:
    sys.path.append(LIB_ROOT)


#fb2lrf
PONYLIB_BIN_FB2LRF = path.join(WINEBIN_ROOT, 'fb2lrf_console', 'fb2lrf_c.exe')
PONYLIB_BIN_FB2LRF_USE_WINE = (platform.system() != 'Window') #Set False on Windows

#wine
PONYLIB_BIN_WINE = '/usr/bin/env wine'

# fulltext search engine
PONYLIB_TEXT_SEARCH_ENGINE = 'ponylib.search.engines.postgre_fts'



# -------------------------------------------
# Django settings


ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS


SITE_ID = 1

USE_I18N = True
USE_L10N = True

# -----------------------------------

AUTOLOAD_SITECONF = 'ponylib.on_load'

MEDIA_ROOT = path.join(VAR_ROOT, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = path.join(VAR_ROOT, 'static-deploy')
STATIC_URL = '/static/'

STATIC_KEY = '001'

ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    path.join(WEB_ROOT, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
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

ROOT_URLCONF = 'ponylib.urls'

TEMPLATE_DIRS = ()

SKIP_SOUTH_TESTS = True

NO_DB_TESTS = False

INSTALLED_APPS = (
    'autoload',
    'ponylib',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django_like',
    'south',
)

# DEBUG
DEBUG = False
TEMPLATE_DEBUG = False

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
# Load additional settings from PROJECT_ROOT/settings/*.py
_additional = [

    #DEBUG
    {
        'key': 'DEBUG',
        'module': 'debug',
        'default': False,
    },

    #TIME_ZONE
    {
        'key': 'TIME_ZONE',
        'module': 'time_zone',
        'default': 'Europe/Moscow'
    },

    #LANGUAGE_CODE
    {
        'key': 'LANGUAGE_CODE',
        'module': 'lang',
        'default': 'en-US',
    },

    #DB
    {
        'key': 'DATABASES',
        'module': 'db',
        'default': {
            'default': {
                # 'postgresql_psycopg2', 'mysql', 'sqlite3' supported
                # 'postgresql_psycopg2' is recomended
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'ponylib',
                'USER': 'ponylib',
                'PASSWORD': '',
                'HOST': '',
                'PORT': '',
            }
        }
    },
]

_bkp_sys_path = sys.path
sys.path = [path.join(PROJECT_ROOT, 'settings')]

for spec in _additional:

    res = None
    try:
       module = importlib.import_module(spec['module'])
       if callable(module.get):
           res = module.get(globals())
       del module

    except ImportError:
        pass

    if res is None:
        res = spec['default']

    globals()[spec['key']] = res

    del spec
    del res

del _additional

sys.path = _bkp_sys_path
del _bkp_sys_path

if DEBUG:
    TEMPLATE_DEBUG = True
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware', )
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar', 'bshell', )
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
        'INTERCEPT_REDIRECTS': False,
    }
