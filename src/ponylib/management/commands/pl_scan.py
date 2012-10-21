# _*_ coding: utf-8 _*_
__license__         = "GPL3"
__copyright__       = "Copyright 2010-2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"

import logging
import os.path as path

from django.core.management.base import BaseCommand

from ponylib.scanner.consumer import AddOrUpdateBookConsumer
from ponylib.scanner import Fb2FilesIterator
from ponylib.scanner.stat import Stat

try:
    from psycopg2 import OperationalError as BadDbError
except ImportError, e:
    from django.db import DatabaseError as BadDbError

class Command(BaseCommand):


    args = '<lib_dir lib_dir ...>'
    help = u'Scan library dirs'
    logger = None

    def handle(self, *args, **options):

        #TODO: use pl_scan_multithread by default. see https://github.com/maizy/PonyLib/issues/48

        self.logger = logging.getLogger('ponylib.scanner')

        lib_paths = map(path.abspath, args)

        stat = Stat()
        stat.start()

        consumer = AddOrUpdateBookConsumer(kwargs={ #multi thread ready consumer
            'connection_alias': 'default',
            'stat': stat})
        consumer.allow_update = False

        iter = Fb2FilesIterator(lib_paths)
        for root_path, rel_path in iter:
            consumer._process_path(root_path, rel_path,
                alias='default', stat=stat)

        stat.end()

        stat.print_report()
        print('\n')
        stat.print_timers()

