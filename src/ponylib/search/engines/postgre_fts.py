# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

from django.dispatch import receiver
from django.db import connection, transaction

from ponylib.models import Book
from ponylib.search.engines import EngineError
from ponylib.search.engines import BaseTextSearchEngine
from ponylib.search.signals import book_index_updated, search_index_dropped

class TextSearchEngine(BaseTextSearchEngine):


    _cursor = None
    _fts_column_name = 'fts'
    _fts_index_name = 'ponylib_book_fts_index'


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
        if book.id is not None:
            self._update_fts_column(book.id)


    def get_simple_book_finder_class(self):
        raise Exception, 'TODO'


    def setup_or_update_engine(self):
        need_commit = False

        if not self._has_fts_column():
            self._add_fts_column()
            self._update_fts_column()
            need_commit = True

        if not self._has_fts_index():
            self._add_fts_index()
            need_commit = True

        if need_commit:
            transaction.commit_unless_managed()

    def drop_engine(self):
        need_commit = False

        if self._has_fts_index():
            self._drop_fts_index()
            need_commit = True

        if self._has_fts_column():
            self._drop_fts_column()
            need_commit = True

        if need_commit:
            transaction.commit_unless_managed()

    def _has_fts_column(self):
        cursor = self._get_cursor()

        cursor.execute(
            'SELECT "column_name" FROM INFORMATION_SCHEMA.COLUMNS'
            ' WHERE "table_name" = %s'
            ' AND "column_name" = %s',
            (Book._meta.db_table, self._fts_column_name)
        )
        if len(list(cursor.fetchall())) > 0:
            return True

        return False

    def _add_fts_column(self):
        self.logger and self.logger.debug('add fts column')
        qn = self._get_qn()
        query = "ALTER TABLE %(table)s ADD COLUMN %(fts_col)s tsvector"
        query = query % {
            'table': qn(Book._meta.db_table),
            'fts_col': qn(self._fts_column_name),
        }
        self._get_cursor().execute(query)

    def _drop_fts_column(self):
        self.logger and self.logger.debug('drop fts column')
        qn = self._get_qn()
        query = "ALTER TABLE %(table)s DROP COLUMN %(fts_col)s"
        query = query % {
            'table': qn(Book._meta.db_table),
            'fts_col': qn(self._fts_column_name),
        }
        self._get_cursor().execute(query)

    def _update_fts_column(self, book_id=None):
        if book_id:
            self.logger and self.logger.debug('update fts field for book.id = %d' % book_id)
        else:
            self.logger and self.logger.debug('update fts column for all books')

        qn = self._get_qn()
        query = 'UPDATE %(table)s SET %(fts_col)s = ' \
                '(' \
                ' setweight( to_tsvector(%%(fts_config)s, "index_a"), %%(a)s )' \
                ' || setweight( to_tsvector(%%(fts_config)s, "index_c"), %%(c)s )' \
                ' )'
        q_params = {
            'fts_config' : self._get_ts_config(),
            'a' : 'A',
            'c' : 'C',
        }

        if book_id is not None:
            query += ' WHERE "id" = %%(book_id)s'
            q_params['book_id'] = book_id

        query = query % {
            'table': qn(Book._meta.db_table),
            'fts_col': qn(self._fts_column_name),
        }

        self._get_cursor().execute(query, q_params)


    def _has_fts_index(self):
        cursor = self._get_cursor()
        cursor.execute(
            'SELECT "relname" FROM "pg_class"'
            ' WHERE "relname" = %s'
            ' AND "oid" IN ('
                'SELECT "indexrelid"'
                ' FROM "pg_index", "pg_class"'
                ' WHERE "pg_class"."relname" = %s'
                ' AND "pg_class"."oid" = "pg_index"."indrelid"'
            ')',
            (self._fts_index_name, Book._meta.db_table)
        )
        if len(list(cursor.fetchall())) > 0:
            return True
        return False

    def _add_fts_index(self):
        self.logger and self.logger.debug('add fts index')
        qn = self._get_qn()
        query = 'CREATE INDEX %(index)s ON %(table)s using %(type)s(%(col)s)'
        query = query % {
            'index': qn(self._fts_index_name),
            'table': qn(Book._meta.db_table),
            'type': self._get_ts_index_type(), #safe
            'col': qn(self._fts_column_name)
        }
        self._get_cursor().execute(query)

    def _drop_fts_index(self):
        self.logger and self.logger.debug('drop fts index')
        query = 'DROP INDEX IF EXISTS %s' % (self._get_qn())(self._fts_index_name)
        self._get_cursor().execute(query)

    def _get_ts_config(self):
        #TODO by def autodetect by current lang
        return self.opts.get('ts_config', 'russian')

    def _get_ts_index_type(self):
        type = self.opts.get('fts_index_type', 'gin').lower()
        if type not in ('gin', 'gist'):
            type = 'gin'
        return type

    def _get_cursor(self):
        if self._cursor is None:
            self._cursor = connection.cursor()
        return self._cursor

    def _get_qn(self):
        return connection.ops.quote_name