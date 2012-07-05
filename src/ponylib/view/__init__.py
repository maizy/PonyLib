# _*_ coding: utf-8 _*_


__license__ = ''
__copyright__ = 'Copyright 2011 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

from django.shortcuts import render_to_response, RequestContext

def debug(request):

    return render_to_response('debug.html', context_instance=RequestContext(request))