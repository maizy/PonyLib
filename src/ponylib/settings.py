# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2011-2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""


import sys
import os.path as path
import platform


# Ponylib settings

PROJECT_ROOT = path.realpath(path.join(path.dirname(__file__), '..', '..'))

WEB_ROOT = path.join(PROJECT_ROOT, 'src', 'ponylib')

VAR_ROOT = path.join(PROJECT_ROOT, 'var')

BIN_ROOT = path.join(PROJECT_ROOT, 'bin')

WINEBIN_ROOT = path.join(PROJECT_ROOT, 'wine_bin')

LIB_ROOT = path.join(PROJECT_ROOT, 'src', 'libs')

#libs
if LIB_ROOT not in sys.path:
    sys.path.append(LIB_ROOT)


#fb2lrf
PONYLIB_BIN_FB2LRF = path.join(WINEBIN_ROOT, 'fb2lrf_console', 'fb2lrf_c.exe')
PONYLIB_BIN_FB2LRF_USE_WINE = (platform.system() != 'Window') #Set False on Windows

#wine
PONYLIB_BIN_WINE = '/usr/bin/env wine'

# Django settings

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS


SITE_ID = 1

USE_I18N = True
USE_L10N = True

# -----------------------------------


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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',

    #'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'ponylib.urls'

TEMPLATE_DIRS = ()

SKIP_SOUTH_TESTS = True

NO_DB_TESTS = False

INSTALLED_APPS = (
    'ponylib',
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    #'django.contrib.messages',
    'django.contrib.staticfiles',
    #'django.contrib.admin',
    'south'
)


# Load additional settings from PROJECT_ROOT/settings/*.py
_additional = [

    #TIME_ZONE
    {
        'key': 'TIME_ZONE',
        'module': 'settings_time_zone',
        'default': None
    },

    #LANGUAGE_CODE
    {
        'key': 'LANGUAGE_CODE',
        'module': 'settings_lang',
        'default': 'en-US',
    },

    #DB
    {
        'key': 'DATABASES',
        'module': 'settings_db',
        'default': {
            'default': {
                'ENGINE': 'django.db.backends.mysql', # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                'NAME': 'ponylib',
                'USER': 'ponylib',
                'PASSWORD': '',
                'HOST': '',
                'PORT': '',
                'OPTIONS' : {
                    'init_command': 'SET storage_engine=INNODB,  SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'
                }
            }
        }
    },

    #Loggind
    {
        'key': 'LOGGING',
        'module': 'settings_logging',
        'default': {
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
    },
]

_bkp_sys_path = sys.path
sys.path = [path.join(PROJECT_ROOT, 'settings')]

for spec in _additional:

    res = None
    try:
       module = __import__(spec['module'], globals(), locals(), [], -1)
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
