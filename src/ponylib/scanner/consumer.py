# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPL v3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

from ponylib.utils.pool import Consumer

class AddOrUpdateBookConsumer(Consumer):

    #TODO update logic
    allow_update=False


    def consume(self):

        files_queue = self.kwargs['files_queue']
        for (lib_path, rel_path) in self.queue_iter(files_queue):
            self.logger('lib: %s, path: %s' % (lib_path, rel_path))





