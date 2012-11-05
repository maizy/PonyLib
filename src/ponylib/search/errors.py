# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

class SearchError(Exception):

    def __init__(self, *args, **kwargs):
        super(SearchError, self).__init__(*args, **kwargs)
        self.finder = None
        self.user_message = _('Unknown error')


class TooShortQuery(SearchError):

    def __init__(self, *args, **kwargs):
        super(TooShortQuery, self).__init__(*args, **kwargs)
        self.min_len = None
        self.user_message = _('All query parts are too short or ignored')


class NoQuery(SearchError):

    def __init__(self, *args, **kwargs):
        super(NoQuery, self).__init__(*args, **kwargs)
        self.user_message = _('Empty query')


class NotSupported(SearchError):

    def __init__(self, *args, **kwargs):
        super(NotSupported, self).__init__(*args, **kwargs)
        self.user_message = _('Feature not supported')


class DbNotSupported(NotSupported):

    def __init__(self, *args, **kwargs):
        super(DbNotSupported, self).__init__(*args, **kwargs)
        self.user_message = _('Feature not supported for your RDBMS')