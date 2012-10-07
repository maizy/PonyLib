# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

from django.dispatch import receiver
from django.db import connection, transaction

from ponylib.models import Book
from ponylib.search.engines import BaseTextSearchEngine
from ponylib.search.signals import book_index_updated, search_index_dropped
from ponylib.search.simple import BaseSimpleBookFinder
from ponylib.search import is_postgre
from ponylib.search.errors import DbNotSupported, TooShortQuery

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
        return SimpleBookFinder


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


class SimpleBookFinder(BaseSimpleBookFinder):

    def _additional_query_check(self):
        if not is_postgre():
            raise DbNotSupported, 'Only Postgre 8.3+'

        fts_config = self.engine._get_ts_config()
#        cursor = connection.cursor()
#        cursor.execute('SELECT count(*) as "cnt" FROM "pg_catalog"."pg_ts_config" WHERE "cfgname" = %s',
#            (fts_config, )
#        )
#        res = cursor.fetchone()
#        if res is None:
#            raise DbNotSupported, 'FTS configuration "%s" not supported at your database' % fts_config
#
#        cursor = connection.cursor()
#        cursor.execute('SELECT count(*) as "cnt" FROM "pg_catalog"."pg_ts_config" WHERE "cfgname" = %s',
#            (fts_config, )
#        )
        cursor = connection.cursor()
        cursor.execute(
            "SELECT numnode(plainto_tsquery(%s, %s))",
            (fts_config, self._get_fts_query())
        )
        res = cursor.fetchone()
        if res is None or int(res[0]) < 1:
            raise TooShortQuery


    def _get_fts_query(self):
        return ' '.join(self.get_query_words())

    def build_queryset(self, limit=None, offset=0):

        """
        @return: Query as Django ORM RawQuerySet
        @rtype: django.db.models.query.RawQuerySet
        """
        self.check_query()
        qn = connection.ops.quote_name

        params={
            'query' : self._get_fts_query(),
            'limit' : limit,
            'offset' : offset,
            'fts_config' : self.engine._get_ts_config(),
        }

        select = 'SELECT *, ts_rank_cd(%(fts_col)s, "fts_q") as "rank"\n' \
                 ' FROM %(table)s,\n' \
                 '   plainto_tsquery(%%(fts_config)s, %%(query)s) as "fts_q"\n' \
                 ' WHERE %(fts_col)s @@ "fts_q" ORDER BY "rank" DESC\n'

        if limit is not None and limit > 0:
            select += ' LIMIT %%(limit)s\n'

        if offset is not None and offset > 0:
            select += ' OFFSET %%(offset)s'

        select = select % {
            'fts_col': qn(self.engine._fts_column_name),
            'table': qn(Book._meta.db_table),
        }

        qs = Book.objects.raw(select, params)
        return qs

    def __len__(self):

        self.check_query()
        qn = connection.ops.quote_name

        params={
            'query' : self._get_fts_query(),
            'fts_config' : self.engine._get_ts_config(),
        }

        select = 'SELECT count(*) as "cnt"\n' \
                 ' FROM %(table)s,\n' \
                 '   plainto_tsquery(%%(fts_config)s, %%(query)s) as "fts_q"\n' \
                 ' WHERE %(fts_col)s @@ "fts_q"'

        select = select % {
            'fts_col': qn(self.engine._fts_column_name),
            'table': qn(Book._meta.db_table),
        }
        cursor = connection.cursor()
        cursor.execute(select, params)
        res = cursor.fetchone()
        if res is not None:
            return int(res[0])
        return 0