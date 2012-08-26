# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__         = "GPL3"
__copyright__       = "Copyright 2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = "Simple SimpleBookFinder for Fast search form"

import re

from django.db.models import Q
from django.utils.text import force_unicode

from ponylib.search.errors import SearchError, NoQuery, TooShortQuery
from ponylib.models import Book
from ponylib.search import escape_for_like

_SPLIT_BY_WORDS_RE = re.compile(r'\s+', re.MULTILINE | re.UNICODE)

MIN_WORD_LEN = 3

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


#    def get_as_dict(self, limit=30, offset=0):
#        """
#
#
#
#        @param limit:
#        @param offset:
#        @return: dict
#        """
#
#        self.check_query()
#        qs = self.get_as_queryset()[offset:limit]
#
#        vals = qs.values()
#
#        return qs and dict(qs[offset:limit]) or None

    def get_query_words(self):

        if self._words is not None:
            return self._words

        query = self.query
        words = re.split(_SPLIT_BY_WORDS_RE, query)
        words = [x for x in words if len(x) >= MIN_WORD_LEN]
        self._words = words

        return words


    def get_as_queryset(self):

        """
        @return: Query as Django ORM QuerySet
        @rtype: django.db.models.query.QuerySet
        """
        self.check_query()

        words = self.get_query_words()

        words_like = '%' + '%'.join([escape_for_like(x) for x in words]) + '%'

        #TODO: add django-like queries with escaping before
        #TODO: use annotation = like '%word1%word2%'
        #TODO: use Concat(`author`, `title`) LIKE '%word1%word2%'
        and_conds = []
        for word in words:
            cond = Q(title__ilike = words_like)
            cond = cond | Q(annotation__ilike = words_like)
            cond = cond | Q(authors__fullname__ilike = words_like)
            and_conds.append(cond)

        qs = Book.objects
        for cond in and_conds:
            qs = qs.filter(cond)

        qs.order_by('title', 'id')
        return qs


    # -------------------------------------------

    @property
    def query(self):
        return self._query

    @property
    def params(self):
        return self._params