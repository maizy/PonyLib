# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__         = "GPLv3"
__copyright__       = "Copyright 2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = "Some test utils and test runner"

import random
import itertools

from django.utils import unittest
from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner

def suite():
    """
    Choose test suite depends on test runner (with db or not)
    @rtype:unittest.TestSuite
    """
    if settings.NO_DB_TESTS:
        return no_db_suite()

    return db_suite()


def db_suite():
    """
    Fully-functional tests, with db access, fixtures etc.
    @rtype:unittest.TestSuite
    """
    from ponylib.tests import search, models, scanner
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromModule(search),
        unittest.TestLoader().loadTestsFromModule(models),
        unittest.TestLoader().loadTestsFromModule(scanner),
    ])
    return suite



def no_db_suite():
    """
    Simple tests, that run without db.
    Check object APIs, std errors etc

    Faster than db_suite.
    @rtype:unittest.TestSuite
    """
    from ponylib.tests import search
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(search.BookFinderApiTestCase),
    ])
    return suite


# -------------------------------------------
# Test runners

class NoDbTestSuiteRunner(DjangoTestSuiteRunner):
    """
    Run django tests without db
    """

    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass


class SearchEngineTestSuiteRunner(DjangoTestSuiteRunner):
    """
    Run django tests with search engine initialization
    """

    def setup_databases(self, **kwargs):
        ret = super(SearchEngineTestSuiteRunner, self).setup_databases(**kwargs)
        from ponylib.search import engines
        engines.engine.setup_or_update_engine()
        return ret

    def teardown_databases(self, old_config, **kwargs):
        try:
            from ponylib.search import engines
            engines.engine.drop_engine()
        except Exception, e:
            pass

        super(SearchEngineTestSuiteRunner, self).teardown_databases(old_config, **kwargs)


# -------------------------------------------
# random text generators

def crange(start, end):
    for c in xrange(ord(start), ord(end) + 1):
        yield unichr(c)


RAND_CHARS = list(itertools.chain(
    crange('a', 'z'), crange('A', 'Z'),
    crange('0', '9'),
    crange('а', 'я'), crange('А', 'Я'), #cyrillic chars
))


def generate_rand_word(len_=10, chars=None):
    if chars is None:
        chars = RAND_CHARS
    return ''.join(random.choice(chars) for x in xrange(len_))


def generate_rand_phrase(len_=3, chars=None):
    if chars is None:
        chars = RAND_CHARS
    words = []
    for w in xrange(len_):
        words.append(generate_rand_word(random.randint(3, 10), chars))
    return ' '.join(words)