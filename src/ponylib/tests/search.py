# _*_ coding: utf-8 _*_


__license__ = ''
__copyright__ = 'Copyright 2011 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

from django.utils import unittest
from django.test import TestCase

from ponylib.search.simple import BookFinder

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

    finder = None

    def setUp(self):
        self.finder = BookFinder()

    def tearDown(self):
        self.finder = None

    def test_instance(self):
        self.assertIsInstance(self.finder, BookFinder)