# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__         = "GPL3"
__copyright__       = "Copyright 2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = "Simple SimpleBookFinder for Fast search form"

import re

from django.db import connection
from django.utils.text import force_unicode

from ponylib.search.errors import SearchError, NoQuery, TooShortQuery, DbNotSupported
from ponylib.models import Book, Author, Series, \
                           BookAuthor, BookSeries
from ponylib.search import escape_for_like, is_sqlite, is_postgre, is_supported_db


_SPLIT_BY_WORDS_RE = re.compile(r'[\s\-\,]+', re.MULTILINE | re.UNICODE)
MIN_WORD_LEN = 3
qn = connection.ops.quote_name

class SimpleBookFinder(object):

    _params = {}
    _query = None
    _words = None

    checked = False


    def __init__(self, **params):
        """
        Init finder.

        One instance should use only once.

        @keyword query: user query
        """
        if 'query' in params:
            self._query = force_unicode(params['query'])
            del params['query']

        self._params = params



    def check_query(self, raise_=True):

        if raise_:
            self._check_query()
        else:
            try:
                return self._check_query()
            except SearchError:
                return False


    def _check_query(self):

        if self.checked:
            return True

        query = self.query

        if not is_supported_db():
            raise DbNotSupported

        # FIXME tmp
        if not is_postgre():
            raise DbNotSupported, 'SQLite and MySql aren\'t supported yet, will be in future releases'


        if query is None or len(query) == 0:
            e = NoQuery()
            e.finder = self
            raise e

        words = self.get_query_words()
        if len(words) == 0:
            e = TooShortQuery()
            e.finder = self
            e.min_len = MIN_WORD_LEN
            raise e

        self.checked = True
        return self.checked


    def get_query_words(self):

        if self._words is not None:
            return self._words

        query = self.query
        words = re.split(_SPLIT_BY_WORDS_RE, query)
        words = [x for x in words if len(x) > 0]

        for word in words:
            if len(word) >= MIN_WORD_LEN:
                return words

        return []


    def get_as_queryset(self, limit = None, offset = None):

        """

        XXX: bad performance query, should be optimized

        @return: Query as Django ORM RawQuerySet
        @rtype: django.db.models.query.RawQuerySet
        """
        self.check_query()

        words = self.get_query_words()

        words_like = '%'.join([escape_for_like(x) for x in words])
        words_like_contains = '%' + words_like + '%'
        words_like_ends = '%' + words_like
        words_like_starts =  words_like + '%'

        # %(param)s - build params
        # %%(param)s - query params
        select_parts = []

        #1. distinct on book.id
        select_parts.append('SELECT DISTINCT on (%(book_t)s.%(id)s)')
        select_parts.append('%(book_t)s.*, ')

        #2.relevance
        relevance_cases = []

        #title same
        relevance_cases.append('%(book_t)s.%(title)s ILIKE %(words_like)s')

        #author + title same
        relevance_cases.append("( %(author_t)s.%(fullname)s || ' ' || %(book_t)s.%(title)s ) ILIKE %(words_like)s")

        #title + author same
        relevance_cases.append("( %(book_t)s.%(title)s || ' ' || %(author_t)s.%(fullname)s ) ILIKE %(words_like)s")

        #title contains
        relevance_cases.append('%(book_t)s.%(title)s ILIKE %(words_like_contains)s')

        #author + title contains
        relevance_cases.append("( %(author_t)s.%(fullname)s || ' ' || %(book_t)s.%(title)s )"
                               " ILIKE %(words_like_contains)s")

        #title + author contains
        relevance_cases.append("( %(book_t)s.%(title)s || ' ' || %(author_t)s.%(fullname)s )"
                               " ILIKE %(words_like_contains)s")

        #author contains
        relevance_cases.append('%(author_t)s.%(fullname)s ILIKE %(words_like_contains)s')

        #series contains
        relevance_cases.append('%(series_t)s.%(name)s ILIKE %(words_like_contains)s')

        select_parts.append('(')

        select_parts.append('CASE')
        cases_amount = len(relevance_cases)
        for ind, case in enumerate(relevance_cases):
            rel_value = cases_amount - ind
            select_parts.append(' WHEN (%s) THEN %d' % (case, rel_value))

        select_parts.append(' ELSE 0 END')
        select_parts.append(') AS %(relevance)s')

        #3.joins
        select_parts.append('FROM %(book_t_fq)s AS %(book_t)s')

        select_parts.append('LEFT OUTER JOIN %(book_author_t_fq)s AS %(book_author_t)s \n'
                            '  ON (%(book_t)s.%(id)s = %(book_author_t)s.%(book_id)s)')

        select_parts.append('LEFT OUTER JOIN %(author_t_fq)s AS %(author_t)s \n'
                            '  ON (%(book_author_t)s.%(author_id)s = %(author_t)s.%(id)s)')

        select_parts.append('LEFT OUTER JOIN %(book_series_t_fq)s AS %(book_series_t)s \n'
                            '  ON (%(book_series_t)s.%(book_id)s = %(book_t)s.%(id)s)')

        select_parts.append('LEFT OUTER JOIN %(series_t_fq)s AS %(series_t)s \n'
                            '  ON (%(book_series_t)s.%(series_id)s = %(series_t)s.%(id)s)')

        #4.match conditions
        select_parts.append('WHERE (')
        #author + title
        select_parts.append('(%(book_t)s.%(title)s || %(author_t)s.%(fullname)s) ILIKE %(words_like_contains)s')
        select_parts.append('OR (%(author_t)s.%(fullname)s || %(book_t)s.%(title)s) ILIKE %(words_like_contains)s')

        #series + author
        select_parts.append('OR (%(series_t)s.%(name)s || %(author_t)s.%(fullname)s) ILIKE %(words_like_contains)s')
        select_parts.append('OR (%(author_t)s.%(fullname)s || %(series_t)s.%(name)s) ILIKE %(words_like_contains)s')

        #serier + title
        select_parts.append('OR (%(series_t)s.%(name)s || %(book_t)s.%(title)s) ILIKE %(words_like_contains)s')
        select_parts.append('OR (%(book_t)s.%(title)s || %(series_t)s.%(name)s) ILIKE %(words_like_contains)s')

        #annotation
        select_parts.append('OR %(book_t)s.%(annotation)s ILIKE %(words_like_contains)s')
        select_parts.append(')')

        #5. wrap on temp table
        select_parts.insert(0, 'SELECT %(tmp)s.* FROM(')
        select_parts.append(') AS %(tmp)s')

        #6.order
        select_parts.append('ORDER BY %(tmp)s.%(relevance)s DESC, %(tmp)s.%(title)s')


        #7. limit, offset
        if limit is not None:
            select_parts.append('LIMIT %(limit)s')

        if offset is not None and offset > 0:
            select_parts.append('OFFSET %(offset)s')


        subs = {}

        qn_subs = {
            'book_t' : 'b',
            'book_author_t' : 'b_a_link',
            'author_t' : 'a',
            'book_series_t' : 'b_s_link',
            'series_t' : 's',
            'tmp' : 'tmp',

            'book_t_fq' : Book._meta.db_table,
            'book_author_t_fq' : BookAuthor._meta.db_table,
            'author_t_fq' : Author._meta.db_table,
            'book_series_t_fq' : BookSeries._meta.db_table,
            'series_t_fq' : Series._meta.db_table,

            'id' : 'id',
            'author_id' : 'author_id',
            'book_id' : 'book_id',
            'series_id' : 'series_id',

            'title' : 'title',
            'annotation' : 'annotation',
            'fullname' : 'fullname',
            'relevance' : 'relevance',
            'name' : 'name',

        }
        subs.update({key:qn(value) for key, value in qn_subs.iteritems()})

        vars_subs = ['words_like', 'words_like_contains', 'words_like_starts',
                     'words_like_ends', 'limit', 'offset']
        subs.update({key:'%('+key+')s' for key in vars_subs})

        select = ' \n'.join(select_parts)

        builded_select = select % subs

        return Book.objects.raw(builded_select, params={
            'words_like' : words_like,
            'words_like_contains' : words_like_contains,
            'words_like_starts' : words_like_starts,
            'words_like_ends' : words_like_ends,
            'limit' : limit,
            'offset' : offset,
        })

    # -------------------------------------------

    @property
    def query(self):
        return self._query

    @property
    def params(self):
        return self._params