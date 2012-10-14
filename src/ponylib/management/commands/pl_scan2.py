# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
__license__         = "GPL v3"
__copyright__       = "Copyright 2010-2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"

import Queue
import os.path as path

from django.core.management.base import BaseCommand

from ponylib.utils.pool import ProducerConsumersPool
from ponylib.scanner.consumer import AddOrUpdateBookConsumer
from ponylib.scanner.producer import Fb2FilesProducer


class Command(BaseCommand):


    args = '<lib_dir lib_dir ...>'
    help = u'Scan library dirs'


    def handle(self, *args, **options):

        lib_paths = map(path.realpath, args)

        pool = ProducerConsumersPool()
        files_queue = Queue.Queue(maxsize=100)

        producer1 = Fb2FilesProducer(kwargs={'lib_paths' : lib_paths, 'file_queue': files_queue})
        producer1.setName('producer1')

        producer2 = Fb2FilesProducer(kwargs={'lib_paths' : lib_paths, 'file_queue': files_queue})
        producer2.setName('producer2')

        pool.add_producer(producer1)
        pool.add_producer(producer2)

        for i in xrange(10):
            consumer = AddOrUpdateBookConsumer(kwargs={'file_queue': files_queue})
            consumer.allow_update = False
            consumer.setName('consumer%2d' % i)
            pool.add_consumer(consumer)

        pool.run()



