# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPV v3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

from fabric.api import local, lcd
from django.conf import settings

def manage(subcomand, args=''):
    with lcd(settings.WEB_ROOT):
        local('./manage.py %s %s' % (subcomand, args))