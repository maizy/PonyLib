# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = "Simple BookFinder for Fast search form"

from django.db.models import Q
from django.utils.text import force_unicode

from ponylib.search.errors import SearchError, NoQuery, TooShortQuery
from ponylib.models import Book

class BookFinder(object):

    _params = {}
    _query = None
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

        if query is None:
            e = NoQuery()
            e.finder = self
            raise e

        if len(query) < 3:
            e = TooShortQuery()
            e.finder = self
            e.expected = 3
            e.actual = len(query)
            raise e

        self.checked = True
        return self.checked


    def get_as_dict(self, limit=30, offset=0):

        self.check_query()
        qs = self.get_as_queryset()
        return qs and dict(qs[offset:limit]) or None


    def get_as_queryset(self):
        """
        @return: Query as Django ORM QuerySet
        @rtype: django.db.models.query.QuerySet
        """
        self.check_query()

        query = self.query

        cond = Q(title__icontains = query)
        cond = cond | Q(authors__fullname__icontains = query)

        qs = Book.objects.filter(cond)
        qs.order_by('title')

        return qs


    # -------------------------------------------

    @property
    def query(self):
        return self._query

    @property
    def params(self):
        return self._params