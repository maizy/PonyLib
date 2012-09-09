# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from django.utils.translation import gettext as _

__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

class SearchError(Exception):

    finder = None
    user_message = 'Unknown error'


class TooShortQuery(SearchError):

    min_len = None

    user_message = 'All query parts are too short or ignored'


class NoQuery(SearchError):

    user_message = 'Empty query'


class NotSupported(SearchError):

    user_message = 'Feature not supported'


class DbNotSupported(NotSupported):

    user_message = 'Feature not supported for your RDBMS'