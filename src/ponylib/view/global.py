# _*_ coding: utf-8 _*_


__license__ = ''
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

import django
from annoying.decorators import render_to

import ponylib

@render_to('debug.html')
def debug(request):

    return {}

@render_to('about.html')
def about(request):

    return {
        'version': {
            'string' : ponylib.__version__
        },
        'authors': ['Nikita Kovaliov'],
        'django_version': django.get_version()
    }

