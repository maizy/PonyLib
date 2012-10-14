# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPV v3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

import os.path as path
from fabric.api import local, lcd
from django.conf import settings

def manage(subcomand, args=''):
    with lcd(settings.WEB_ROOT):
        manage_path = path.join(settings.LIB_ROOT, 'manage.py')
        local('%s %s %s' % (manage_path, subcomand, args))