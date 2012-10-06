# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = 'Code that run once before any HTTP request or command execution'

import logging
import ponylib.search.engines

def init_text_search_engine():
    logger = logging.getLogger('ponylib.search.engines')
    try:
        engine = ponylib.search.engines.build_default_engine()
    except ponylib.search.engines.EngineError, e:
        logger.error(e.message)
        return False

    ponylib.search.engines.engine = engine
    engine.register_signals()

    return True

logger = logging.getLogger('ponylib.on_load')

logger.debug('init text search engine')
init_text_search_engine()