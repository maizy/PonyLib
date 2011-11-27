# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext


def index(request):

    c = {}
    return render_to_response('search/index_n_results.html', c, context_instance=RequestContext(request))


def results(request):

    return HttpResponse(u'Ping-pong')