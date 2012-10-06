# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

import abc
import logging

from ponylib.search.errors import SearchError

class EngineError(SearchError):
    pass

class BaseTextSearchEngine(object):

    __metaclass__ = abc.ABCMeta

    logger = None

    def __init__(self):
        self.logger = logging.getLogger('ponylib.search.engines')
        self.logger.debug('%s.%s inited' % (self.__module__, self.__class__.__name__))

    def register_signals(self):
        """Register all engine's signals"""
        pass

    @abc.abstractmethod
    def build_simple_book_finder(self):
        """
        @rtype: ponylib.search.simple.SimpleBookFinder
        """
        pass

    def setup_or_update_engine(self):
        """Init or update engine backend"""
        pass

    def drop_engine(self):
        """Drop engine backend"""
        pass


def build_default_engine():
    from importlib import import_module

    try:
        from django.conf import settings
        engine_name = settings.PONYLIB_TEXT_SEARCH_ENGINE
    except (ImportError, AttributeError):
        raise EngineError, 'django setting "PONYLIB_TEXT_SEARCH_ENGINE" not found'

    try:
        engine_module = import_module(engine_name)
    except ImportError:
        raise EngineError, 'Unable to load text search engine "%s"' % engine_name

    try:
        engine = engine_module.TextSearchEngine()
    except AttributeError:
        raise EngineError, 'Unable to init text search engine class "%s.TextSearchEngine"' % engine_name

    return engine

# normaly inited at ponylib.on_load
engine = None