# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

from django.http import HttpResponse


def index(request):

    return HttpResponse(u'Beep-beep')


def results(request):

    return HttpResponse(u'Ping-pong')