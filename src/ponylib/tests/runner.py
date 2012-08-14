# _*_ coding: utf-8 _*_


__license__ = ''
__copyright__ = 'Copyright 2011 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

from django.test.simple import DjangoTestSuiteRunner

class NoDbTestSuiteRunner(DjangoTestSuiteRunner):
    """
    Run django tests without db
    """

    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass