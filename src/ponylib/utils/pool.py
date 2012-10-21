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
    logger_name = None
    logger = None

    def __init__(self, group=None, target=None, name=None, kwargs=None, verbose=None):

        if name is None:
            name = self.def_name

        logger_name = self.logger_name
        if logger_name is None:
            logger_name = self.__module__ + '.' + self.__class__.__name__
        self.logger = logging.getLogger(logger_name)

        super(ThreadWithKwargs, self).__init__(group=group, target=target, name=name, verbose=verbose)

        if kwargs is None:
            kwargs = {}
        self.kwargs = kwargs

    def is_interrupt(self):
        return self.stop_token is not None and self.stop_token.stop


class Consumer(ThreadWithKwargs):

    __metaclass__ = abc.ABCMeta
    producers_done_event = None
    _sleep_time = 0.2

    def __init__(self, group=None, target=None, name=None, kwargs=None, verbose=None):
        super(Consumer, self).__init__(group, target, name, kwargs, verbose)
        self.producers_done_event = Event()

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
#                self.logger.debug('wait for queue values')
                time.sleep(self._sleep_time)

        raise StopIteration


class Producer(ThreadWithKwargs):

    __metaclass__ = abc.ABCMeta
    _sleep_time = 1
    done_event = None

    def __init__(self, group=None, target=None, name=None, kwargs=None, verbose=None):
        super(Producer, self).__init__(group, target, name, kwargs, verbose)
        self.done_event = Event()

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
                self.after_value_pushed(value)
                break
            except Queue.Full:
                time.sleep(self._sleep_time)
        return interrupt

    def after_value_pushed(self, value):
        pass


class ProducerConsumersPool(object):

    producers_done_event = None
    stop_token = None
    logger = None

    producers = None
    consumers = None

    _editable = True
    _sleep_time = 0.5

    def __init__(self):
        self.producers_done_event = Event()
        self.stop_token = StopToken()
        self.producers = []
        self.consumers = []
        self.logger = logging.getLogger('ponylib.pool')

    def add_producer(self, producer):
        if not self.editable:
            raise PoolLocked
        producer.setDaemon(True)
        self.producers.append(producer)
        return self


    def add_consumer(self, consumer):
        if not self.editable:
            raise PoolLocked
        consumer.producers_done_event = self.producers_done_event
        consumer.stop_token = self.stop_token
        consumer.setDaemon(True)
        self.consumers.append(consumer)
        return self

    def run(self):
        self._editable = False

        for producer in self.producers:
            producer.start()
        for consumer in self.consumers:
            consumer.start()

        try:
            #don't block main thread, check system signals sometimes
            while self._any_more():
                time.sleep(self._sleep_time)
        except KeyboardInterrupt:
            self.stop_token.stop = True
            self.logger.debug('Pool was interrupted')

    def _any_more(self):
        p_event = self.producers_done_event
        if p_event.is_set():
            any_more = False
        else:
            all_producers_done = True
            for producer in self.producers:
                if not producer.done_event.is_set():
                    all_producers_done = False
                    break
            any_more = not all_producers_done
            if all_producers_done and not p_event.is_set():
                p_event.set()
                self.logger.debug('All producers done, wait for consumers')

        if not any_more:
            #check consumer treads
            for consumer in self.consumers:
                if consumer.is_alive():
                    any_more = True
                    break
            if not any_more:
                self.logger.debug('All consumers done')
        return any_more


    @property
    def editable(self):
        return self._editable


