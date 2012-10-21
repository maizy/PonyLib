# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = ''
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

from fabric.api import task
from ponylib.fab import manage as _manage

@task
def shell():
    """Django shell"""
    _manage('shell')
