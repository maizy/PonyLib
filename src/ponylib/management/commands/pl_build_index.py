# _*_ coding: utf-8 _*_
from __future__ import unicode_literals


__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

import sys
from math import ceil

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.db import connection, transaction
from django.db.models import Q
from ponylib.models import Book

qn = connection.ops.quote_name

class Command(BaseCommand):

    help = _('Build search index (for not indexed books only)')

    def handle(self, *args, **options):
        try:
            cursor = connection.cursor()
            get_ids_query = 'SELECT %(id)s FROM %(table)s WHERE %(index_a)s = %%s AND %(index_c)s = %%s'
            get_ids_query = get_ids_query % {
                'table' : qn(Book._meta.db_table),
                'id' : qn('id'),
                'index_a' : qn('index_a'),
                'index_c' : qn('index_c'),
            }
            cursor.execute(get_ids_query, ('',''))
            all_ids = cursor.fetchall()
            total = len(all_ids)

            sys.stdout.write(_('Build search index')+'\n')
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
                    book.save()
                    sys.stdout.write('.')
                except Book.DoesNotExist: #when processing book may deleted
                    sys.stdout.write('-')

                sys.stdout.flush()

                if (total > 500 and cnt % dec == 0) or cnt == total:
                    sys.stdout.write('\n%5d / %5d  (%2d%%)\n' % (cnt, total, ceil(float(cnt)*100/float(total))))
                    sys.stdout.flush()

                cnt += 1

            sys.stdout.write('\n' + _('Done'))

        except KeyboardInterrupt:
            sys.stdout.write('\n' + _('Aborted'))

