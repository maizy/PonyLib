# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__         = "GPL3"
__copyright__       = "Copyright 2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = "Simple SimpleBookFinder for Fast search form"

import re
import abc

from django.utils.text import force_unicode

from ponylib.search.errors import SearchError, NoQuery, TooShortQuery, DbNotSupported
from ponylib.search import is_supported_db


_SPLIT_BY_WORDS_RE = re.compile(r'[\s\-\,]+', re.MULTILINE | re.UNICODE)
MIN_WORD_LEN = 3

class _Finder(object):

    # -------------------------------------------
    # pagination support

    def count(self):
        return len(self)

    def __getitem__(self, k):

        if not isinstance(k, (slice, int, long)):
            raise TypeError

        assert ((not isinstance(k, slice) and (k >= 0))
                or (isinstance(k, slice) and (k.start is None or k.start >= 0)
                    and (k.stop is None or k.stop >= 0))), \
                "Negative indexing is not supported."

        offset = 0
        limit = None

        if isinstance(k, slice):
            if k.start is not None:
                offset = int(k.start)

            if k.stop is not None:
                limit = int(k.stop) - offset
        else:
            limit = 1
            offset = k

        return self.build_queryset(limit, offset)

    @abc.abstractmethod
    def build_queryset(self, limit=None, offset=0):
        raise SearchError('Not implemented')

    @abc.abstractmethod
    def __len__(self):
        raise SearchError('Not implemented')



class SimpleBookFinder(_Finder):

    """\
    Base class for simple one line query finder
    """

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

        self._additional_query_check()

        self.checked = True

        return self.checked

    def _additional_query_check(self):
        """Subclasses may raise SearchError for wrong queries"""
        pass

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

    # -------------------------------------------

    @property
    def query(self):
        return self._query

    @property
    def params(self):
        return self._params


def get_simple_finder_class():
    import ponylib.search.naive
    return ponylib.search.naive.NaiveLikeSimpleBookFinder