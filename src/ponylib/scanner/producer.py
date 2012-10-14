# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = ''
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''


from ponylib.utils.pool import Producer
from ponylib.scanner import Fb2FilesIterator


class Fb2FilesProducer(Producer):

    def_name = 'fb2_files_producer'

    def produce(self):
        #args not checked here
        files_queue = self.kwargs['files_queue']
        lib_paths = self.kwargs['lib_paths']

        iter = Fb2FilesIterator(lib_paths)
        self.queue_push_from_iter(files_queue, iter)

