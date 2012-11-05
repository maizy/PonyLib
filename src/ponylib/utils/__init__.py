# _*_ coding: utf-8 _*_
from __future__ import division

__license__ = 'GPL v3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

import math

def group(list_, groups_amount):
    # FIXME group(range(9), 4) = [[0, 1, 2], [3, 4, 5], [6, 7, 8]] :)
    if groups_amount <= 0:
        raise ValueError('groups_amount must be great than 0')
    by_step = max(int(math.ceil(len(list_)/groups_amount)), 1)
    for i in xrange(0, len(list_), by_step):
        yield list_[i:i+by_step]