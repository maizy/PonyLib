# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from __future__ import division

__license__ = 'GPL v3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

import datetime

class Stat(object):

    book_processed = 0

    start_time = None
    end_time = None

    def start(self):
        self.start_time = datetime.datetime.now()

    def end(self):
        self.end_time = datetime.datetime.now()

    def get_report(self):

        print('Books processed: %d' % self.book_processed)

        if self.start_time is not None and self.end_time is not None:
            total = self.end_time - self.start_time
            total_sec = total.total_seconds()
            print('Total time: %d sec' % total_sec)
            if self.book_processed > 0:
                bps = self.book_processed / total_sec
                print('Book per second: %0.4f' % bps)

    def add_book_stat(self):
        #FIXME non thread safe
        self.book_processed += 1