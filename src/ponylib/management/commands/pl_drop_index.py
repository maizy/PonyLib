# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

import sys

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from ponylib.models import Book
from ponylib.management import yn

class Command(BaseCommand):

    help = _('Drop search index')

    def handle(self, *args, **options):

        if yn(_('Are you sure? All search index will be dropped. This can not be undone.')):
            sys.stdout.write(_('Drop index ... '))
            sys.stdout.flush()
            Book.objects.all().update(index_a='', index_c='')
            sys.stdout.write(_('OK') + '\n')
            sys.stdout.flush()

        else:
            print(_('Cancelled'))

