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


from fabric.api import local, lcd
from fabric.contrib import django
django.settings_module('ponylib.settings')

from django.conf import settings

def locales_up():
    """Update locales"""
    with lcd(settings.WEB_ROOT):
        local('./manage.py makemessages -l en_US')
        local('./manage.py makemessages -l ru_RU')

def locales_co():
    """Compile locale messages"""
    with lcd(settings.WEB_ROOT):
        local('./manage.py compilemessages')

def testf():
    """Fast tests (no db)"""
    with lcd(settings.LIB_ROOT):
        local('./manage.py test ponylib --settings=ponylib.settings_no_db_tests')

def test():
    """All tests"""
    with lcd(settings.LIB_ROOT):
        local('./manage.py test ponylib')
