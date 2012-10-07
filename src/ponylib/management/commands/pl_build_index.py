# _*_ coding: utf-8 _*_
from __future__ import unicode_literals


__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.db import connection
from ponylib.models import Book
from ponylib.management import rebuild_search_index

class Command(BaseCommand):

    help = _('Build search index (for not indexed books only)')

    def handle(self, *args, **options):

        qn = connection.ops.quote_name
        query = 'SELECT %(id)s FROM %(table)s WHERE %(index_a)s = %%s AND %(index_c)s = %%s'
        query = query % {
            'table' : qn(Book._meta.db_table),
            'id' : qn('id'),
            'index_a' : qn('index_a'),
            'index_c' : qn('index_c'),
        }

        args = ('','')

        rebuild_search_index(query, args, self.help)




