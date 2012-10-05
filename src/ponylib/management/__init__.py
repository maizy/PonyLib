# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__         = "GPLv3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

import sys

def yn(message = '', default = False):
    """Read y/n user input"""

    if len(message) > 0:
        sys.stdout.write('%s %s'  % (message, default and '[n/Y]' or '[y/N] '))

    res = raw_input().decode(sys.stdin.encoding)
    res = res.strip().lower()

    if res in ('y', '1', 'yes', 'ys',):
        result = True
    elif res in ('n', '0', 'no',):
        result = False
    else:
        result = default

    return result


