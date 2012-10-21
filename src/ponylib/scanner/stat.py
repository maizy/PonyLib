# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from __future__ import division

__license__ = 'GPL v3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

import datetime
import sys
from collections import Counter

class Stat(object):

    book_processed = 0

    start_time = None
    end_time = None
    _timers = None
    _timers_sum = None
    _next_timer_id = 0
    print_process_status = True

    def __init__(self):
        self._timers = {}
        self._timers_sum = Counter()


    def start(self):
        self.start_time = datetime.datetime.now()

    def end(self):
        self.end_time = datetime.datetime.now()

        if self.print_process_status:
            print(' Done\n')

    def timer(self, key):
        timer_id = self._next_timer_id
        self._next_timer_id += 1
        self._timers[timer_id] = (datetime.datetime.now(), key)
        def stop():
            self._stop_timer(timer_id)
        return stop

    def add_book_stat(self):
        #FIXME non thread safe
        self.book_processed += 1
        if self.print_process_status:
            sys.stdout.write('.')
            sys.stdout.flush()

    # -------------------------------------------

    def get_total_time(self):
        if self.start_time is None:
            return 0
        if self.end_time is None:
            end = datetime.datetime.now()
        else:
            end = self.end_time
        return (end - self.start_time).total_seconds()

    def stop_all_timers(self):
        for timer_id in self._timers.keys():
            self._stop_timer(timer_id)

    def get_report(self):
        report = ''
        report += 'Books processed: %d\n' % self.book_processed
        if self.start_time is not None and self.end_time is not None:
            total = self.end_time - self.start_time
            total_sec = total.total_seconds()
            report += 'Total time: %d sec\n' % total_sec
            if self.book_processed > 0:
                bps = self.book_processed / total_sec
                report +='Book per second: %0.4f\n' % bps

        return report.rstrip('\n')

    def print_report(self):
        if self.print_process_status:
            print(self.get_report())

    def print_timers(self):
        total = self.get_total_time()
        for key, value in self._timers_sum.most_common():

            print('%s => %f0.4 (%2.0f%%)' % (
                key, value, value/total*100
            ))

    def _stop_timer(self, timer_id):
        if timer_id in self._timers:
            start, key = self._timers[timer_id]
            self._timers_sum[key] += max(0, (datetime.datetime.now() - start).total_seconds())
            del self._timers[timer_id]
            return True
        return False

