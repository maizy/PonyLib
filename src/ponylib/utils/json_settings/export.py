# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = 'Load and parse json settings as module variables for from ... import *'

from ponylib.utils.json_settings import settings_path as _settings_path
from ponylib.utils.json_settings import parse_json_with_comments as _parse_json_with_comments

# no additional key checks here
# json structure should be valid
_settings = _parse_json_with_comments(_settings_path)

#import upprint
#upprint.pprint(_settings)

DATABASES = {
    'default': {
        'ENGINE': _settings['db']['django_engine'],
        'NAME': _settings['db']['database'],
        'USER': _settings['db']['user'],
        'PASSWORD': _settings['db']['password'],
        'HOST': _settings['db']['host'],
        'PORT': _settings['db']['port'],
    }
}

LANGUAGE_CODE = _settings['local']['default_language']
TIME_ZONE = _settings['local']['time_zone']
SECRET_KEY = _settings['secret_key']

PONYLIB_TEXT_SEARCH_ENGINE = _settings['search']['engine']
PONYLIB_TEXT_SEARCH_ENGINE_OPTS = _settings['search'].get('engine_opts', {})

# debug section may be omitted
_debug_section = _settings.get('debug')
if _debug_section is not None:
    try:
        DEBUG = _debug_section.get('django_debug')
        DEBUG_TOOLBAR = _debug_section.get('django_debug_toolbar')
    except AttributeError:
        pass


#remove unused vars
del _settings_path
del _settings
del _parse_json_with_comments
del _debug_section