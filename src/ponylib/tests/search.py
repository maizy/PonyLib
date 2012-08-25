# _*_ coding: utf-8 _*_

from __future__ import unicode_literals

__license__ = ''
__copyright__ = 'Copyright 2011 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

from django.utils import unittest
from django.test import TestCase

from ponylib.search.simple import SimpleBookFinder, MIN_WORD_LEN
import ponylib.search.errors as search_errors

#class BookFinderDbTestCase(TestCase):
#
#    def setUp(self):
#        pass
#
#    def tearDown(self):
#        pass
#


class BookFinderApiTestCase(unittest.TestCase):
    """
    Simple test case that perform without db access.

    Check api, errors etc.
    """

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_set_query(self):

        test_query_str = b'test query'
        test_query_unicode = 'test query'

        finder = SimpleBookFinder(query=test_query_unicode)
        self.assertEqual(finder.query, test_query_unicode)

        finder = SimpleBookFinder(query=test_query_str)
        self.assertIsInstance(finder.query, unicode, 'Str should convert to unicode')



    def test_short_query(self):

        short_q, exception_ = self.perform_short_q()

        self.assertIsNotNone(exception_.min_len, MIN_WORD_LEN)


    def test_check_query_not_raised(self):
        short_q = self.perform_short_q()[0]

        #should not raised
        try:
            short_q.check_query(raise_=False)
        except search_errors.SearchError:
            self.fail('check_query(raise_=True) should\'t raised SearchError')


    def test_empty_query(self):

        empty_q = SimpleBookFinder()
        with self.assertRaises(search_errors.NoQuery):
            empty_q.check_query()

        empty_q2 = SimpleBookFinder(query='')
        with self.assertRaises(search_errors.NoQuery):
            empty_q2.check_query()


    def test_query_split(self):
        fixtures = [
            ('some', ['some'], None),
            ('apple orange', ['apple', 'orange'], 'words should be splited'),
            ('абвг\nabcd', ['абвг', 'abcd'], 'new line should be ignored and process as space'),
            ('zx\nabcd', ['abcd'], 'short words should be ignored'),
        ]

        for query, expected, mes in fixtures:
            finder = SimpleBookFinder(query=query)
            actual = finder.get_query_words()
            self.assertEqual(expected, actual, mes)

    # -------------------------------------------

    def perform_short_q(self):

        short_q = SimpleBookFinder(query='42')
        with self.assertRaises(search_errors.TooShortQuery) as e:
            short_q.check_query()
        exception_ = e.exception
        return short_q, exception_

