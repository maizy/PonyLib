# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPL v3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = 'Threading process helpers and base classes'

from threading import Thread, Event
import logging
import time
import abc
import Queue


class StopToken(object):
    stop = False


class PoolLocked(Exception):
    pass


class ThreadWithKwargs(Thread):

    kargs = None
    def_name = None
    stop_token = None

    def __init__(self, group=None, target=None, name=None, kwargs=None, verbose=None):

        if name is None:
            name = self.def_name

        super(ThreadWithKwargs, self).__init__(group=group, target=target, name=name, verbose=verbose)

        if kwargs is None:
            kwargs = {}
        self.kwargs = kwargs

    def is_interrupt(self):
        return self.stop_token is not None and self.stop_token.stop


class Consumer(ThreadWithKwargs):

    __metaclass__ = abc.ABCMeta
    producers_done_event = None
    logger = None

    _sleep_time = 0.4

    def __init__(self, group=None, target=None, name=None, kwargs=None, verbose=None):
        super(Consumer, self).__init__(group, target, name, kwargs, verbose)
        self.producers_done_event = Event()
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self):
        self.consume()

    @abc.abstractmethod
    def consume(self):
        pass

    def queue_iter(self, queue):
        """Iterate over producer queue"""
        queue_empty = False
        while not self.is_interrupt():
            value = None
            try:
                value = queue.get_nowait()
            except Queue.Empty:
                if self.producers_done_event.is_set():
                    queue_empty = True
            if value is not None:
                yield value

            if queue_empty:
                break
            else:
                time.sleep(self._sleep_time)

        raise StopIteration


class Producer(ThreadWithKwargs):

    __metaclass__ = abc.ABCMeta
    _sleep_time = 1
    done_event = None
    logger = None

    def __init__(self, group=None, target=None, name=None, kwargs=None, verbose=None):
        super(Producer, self).__init__(group, target, name, kwargs, verbose)
        self.done_event = Event()
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self):
        self.produce()
        self.done_event.set()

    @abc.abstractmethod
    def produce(self):
        pass

    def queue_push_from_iter(self, queue, iter):
        interrupt = False
        for value in iter:
            interrupt = self.queue_push(queue, value)
            if interrupt:
                break
        return interrupt

    def queue_push(self, queue, value):
        #put loop
        interrupt = False
        while True:
            if self.is_interrupt():
                interrupt = True
                break
            try:
                queue.put_nowait(value)
                break
            except Queue.Full:
                time.sleep(self._sleep_time)
        return interrupt


class ProducerConsumersPool(object):

    producers_done_event = None
    stop_token = None

    producers = None
    consumers = None

    _editable = True

    def __init__(self):
        self.producers_done_event = Event()
        self.stop_token = StopToken()
        self.producers = []
        self.consumers = []

    def add_producer(self, producer):
        if not self.editable:
            raise PoolLocked
        self.producers.append(producer)
        return self


    def add_consumer(self, consumer):
        if not self.editable:
            raise PoolLocked
        consumer.producers_done_event = self.producers_done_event
        consumer.stop_token = self.stop_token
        self.consumers.append(consumer)
        return self

    def run(self):
        self._editable = False

    @property
    def editable(self):
        return self._editable


