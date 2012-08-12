# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

from upprint import pformat

from annoying.decorators import render_to
from django.utils.translation import gettext as _
from django.conf import settings

@render_to('search/search_form.html')
def index(request):

    c = {
        'page': {
            'title': _('Search'),
        },
        'disable_quick_search' : True,
    }

    return c

@render_to('search/results.html')
def results(request):

    c = {
        'page': {
            'title': _('Search Results'),
        }
    }

    #use post, than get
    request_qdict = request.REQUEST

    type = request_qdict.get('type', u'simple')
    if type not in ['simple', 'adv']:
        type = 'simple'

    c['type'] = type

    if settings.DEBUG:
        c['debug'] = {'params' : pformat(request_qdict)}

    return c