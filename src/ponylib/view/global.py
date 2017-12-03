# _*_ coding: utf-8 _*_


__license__ = ''
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

import django
from annoying.decorators import render_to

import ponylib
from ponylib.view import check_password, set_password


@render_to('debug.html')
def debug(request):
    check_password(request)
    return {}


@render_to('about.html')
def about(request):
    check_res = check_password(request)
    if check_res is not None:
        return check_res
    return {
        'version': {
            'string' : ponylib.__version__
        },
        'authors': ['Nikita Kovaliov'],
        'django_version': django.get_version()
    }


@render_to('auth.html')
def auth(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        return set_password(password)
    return {}
