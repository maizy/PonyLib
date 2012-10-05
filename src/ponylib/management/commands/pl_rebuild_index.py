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

    help = _('Rebuild search index')

    def handle(self, *args, **options):

        qn = connection.ops.quote_name
        query = 'SELECT %(id)s FROM %(table)s ORDER BY %(id)s'
        query = query % {
            'table' : qn(Book._meta.db_table),
            'id' : qn('id'),
        }

        args = ('','')

        rebuild_search_index(query, args, self.help)




