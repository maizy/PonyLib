# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPL v3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = 'Fabric file for ponylib'

import sys
import os.path as path
sys.path.append(path.join(path.dirname(__file__), 'src'))


from fabric.api import local, lcd, warn, abort, task
from fabric.contrib import django
django.settings_module('ponylib.settings')

from ponylib.fab import manage as _manage

#modules
from ponylib.fab import lc, test, d

# -------------------------------------------

@task
def scan(*roots):
    """Add books to library"""
    if len(roots) == 0:
        abort('Usage:   fab scan:ROOT_PATH[,ROOT_PATH...]')

    call_roots = []
    for root in roots:
        if path.exists(root):
            call_roots.append(path.abspath(root))
        else:
            abort('Path %s not exists' % root)

    _manage('pl_scan', "'%s'" % "' '".join(call_roots))

