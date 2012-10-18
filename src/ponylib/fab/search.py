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
def setup_engine():
    """Init or update search engine"""
    _manage('pl_setup_ts_engine')
    build_index()


@task
def drop_engine():
    """Init or update search engine"""
    _manage('pl_drop_ts_engine')


@task
def build_index(force=False):
    """Update search index"""
    if force:
        _manage('pl_rebuild_index')
    else:
        _manage('pl_build_index')


@task
def drop_index(force=False):
    """Drop search index"""
    _manage('pl_drop_index')
