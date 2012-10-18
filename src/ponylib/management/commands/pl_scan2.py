# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
__license__         = "GPL v3"
__copyright__       = "Copyright 2010-2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"

import sys
import logging
import Queue
import os.path as path

from django.conf import settings
from django.core.management.base import BaseCommand
import django.db

from ponylib.utils.pool import ProducerConsumersPool
from ponylib.scanner.consumer import AddOrUpdateBookConsumer
from ponylib.scanner.producer import Fb2FilesProducer
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

        self.logger = logging.getLogger('ponylib.scanner')

        #TODO shared connections pool
        connections = self.prepare_and_check_db_connections()

        lib_paths = map(path.abspath, args)

        stat = Stat()
        stat.start()

        pool = ProducerConsumersPool()
        files_queue = Queue.Queue(maxsize=100)

        for i, lib_path in enumerate(lib_paths, start=1):
            producer = Fb2FilesProducer(kwargs={
                'lib_paths' : [lib_path],
                'files_queue': files_queue,
                'stat': stat})
            producer.setName('producer%02d' % i)
            pool.add_producer(producer)

        for i in xrange(1, settings.PONYLIB_SCAN_THREADS+1):
            consumer = AddOrUpdateBookConsumer(kwargs={
                'files_queue': files_queue,
                'connection_alias': connections.pop(),
                'stat': stat})
            consumer.allow_update = False
            consumer.setName('consumer%02d' % i)
            pool.add_consumer(consumer)

        pool.run()

        stat.end()
        print(stat.get_report())



    # -------------------------------------------


    def prepare_and_check_db_connections(self):

        assert (settings.PONYLIB_SCAN_THREADS == settings.PONYLIB_SCAN_CONCURENT_CONNECTIONS_AMOUNT)
        connections = settings.DATABASES.keys()
        connections = [x for x in connections if x == 'default' or x.startswith('additional_')]
        assert (len(connections) == settings.PONYLIB_SCAN_THREADS)
        #force open django connections
        opened = 0
        try:
            for alias in connections:
                django.db.connections[alias].cursor().execute('SELECT 1')
                opened += 1
        except BadDbError, e:
            err = \
                'Unable to open enougth database connections.\n'\
                'Need %d, successfully opened %d.\n' % (len(connections), opened)

            suggest = \
                'Increase you database "max_connection" setting or ' \
                'decreate "scan.concurent_connections_amount" in settings.json.\n' \
                '\n'

            db_err = 'Db Error: %s' % e.message

            self.logger.fatal((err + db_err).replace('\n', ' '))
            sys.stderr.write(err + suggest + db_err)
            sys.exit(2)

        return connections



