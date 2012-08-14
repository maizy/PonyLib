# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""


from ponylib.settings import *

TEST_RUNNER = 'ponylib.tests.runner.NoDbTestSuiteRunner'
SOUTH_TESTS_MIGRATE = False
NO_DB_TESTS = True