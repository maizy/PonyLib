# _*_ coding: utf-8 _*_

__license__         = "GPLv3"
__copyright__       = "Copyright 2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

from django.utils import unittest
from django.conf import settings

import search

def suite():
    """
    Choose test suite depends on test runner (with db or not)
    @return:unittest.TestSuite
    """
    if settings.NO_DB_TESTS:
        return no_db_suite()

    return db_suite()


def db_suite():
    """
    Fully-functional tests, with db access, fixtures etc.
    @return:unittest.TestSuite
    """

    search_tests_suite = unittest.TestLoader().loadTestsFromModule(search)

    suite = unittest.TestSuite([search_tests_suite])
    return suite



def no_db_suite():
    """
    Simple tests, that run without db.
    Check object APIs, std errors etc

    Faster than db_suite.
    @return:unittest.TestSuite
    """

    search_tests_suite = unittest.TestLoader().loadTestsFromTestCase(search.BookFinderApiTestCase)

    suite = unittest.TestSuite([search_tests_suite])
    return suite