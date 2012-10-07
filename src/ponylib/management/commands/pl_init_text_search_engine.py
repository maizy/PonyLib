# _*_ coding: utf-8 _*_
from __future__ import unicode_literals


__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

import ponylib.search.engines as engines

class Command(BaseCommand):

    help = _('Init text search engine')

    def handle(self, *args, **options):
        print(self.help)
        engines.engine.setup_or_update_engine()
        print(_('Done'))






