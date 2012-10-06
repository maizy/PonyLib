# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

from django.dispatch import receiver

from ponylib.search.engines import BaseTextSearchEngine
from ponylib.search.signals import book_index_updated, search_index_dropped

class TextSearchEngine(BaseTextSearchEngine):

    def register_signals(self):

        @receiver(book_index_updated, weak=False)
        def proxy(sender, **args):
            if 'book' in args:
                return self.update_fts_field(args['book'])

        self.logger and \
            self.logger.debug('connect to book_index_updated event')

        @receiver(search_index_dropped, weak=False)
        def proxy(sender, **args):
            return self._update_fts_column()

        self.logger and \
            self.logger.debug('connect to search_index_dropped event')

    def update_fts_field(self, book):
        self.logger and self.logger.debug('update fts field for book.id = %d' % book.id)

    def build_simple_book_finder(self):
        raise Exception, 'TODO'

    def _add_fts_column(self):
        self.logger and self.logger.debug('add fts column')

    def _drop_fts_column(self):
        self.logger and self.logger.debug('drop fts column')

    def _add_fts_index(self):
        self.logger and self.logger.debug('add fts index')

    def _drop_fts_index(self):
        self.logger and self.logger.debug('drop fts index')

    def _update_fts_column(self):
        self.logger and self.logger.debug('update fts column')
