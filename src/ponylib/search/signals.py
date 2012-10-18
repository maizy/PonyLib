# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

from django.dispatch import Signal

book_index_updated = Signal(providing_args=('book', 'using' ))

search_index_dropped = Signal()

