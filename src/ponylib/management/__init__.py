# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__         = "GPLv3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

import sys
from math import ceil

from django.utils.translation import ugettext as _
from django.db import connection
from ponylib.models import Book

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

def rebuild_search_index(query, query_args, action_message = ''):

    cursor = connection.cursor()

    try:
        cursor.execute(query, query_args)
        all_ids = cursor.fetchall()
        total = len(all_ids)

        sys.stdout.write(action_message+'\n')
        sys.stdout.write(_('Total records which will be updated: %s') % total + '\n')
        cnt = 1
        if total > 1000:
            steps = 100
        else:
            steps = 20

        dec = max(total / steps, 1)

        for (id,) in all_ids:
            try:
                book = Book.objects.get(pk=id)
                book.update_search_index()
                sys.stdout.write('.')
            except Book.DoesNotExist: #when processing book may be deleted
                sys.stdout.write('-')

            sys.stdout.flush()

            if (total > 500 and cnt % dec == 0) or cnt == total:
                sys.stdout.write('\n%5d / %5d  (%2d%%)\n' % (cnt, total, ceil(float(cnt)*100/float(total))))
                sys.stdout.flush()

            cnt += 1

        sys.stdout.write('\n' + _('Done') + '\n')

    except KeyboardInterrupt:
        sys.stdout.write('\n' + _('Aborted') + '\n')


