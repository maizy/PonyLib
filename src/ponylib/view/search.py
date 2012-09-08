# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__         = "GPL3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

import collections
from upprint import pformat

from annoying.decorators import render_to
from django.utils.translation import gettext as _
from django.utils.text import force_unicode
from django.conf import settings

from ponylib.search.simple import SimpleBookFinder

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
        },
        'debug' : {},
    }

    #use post, than get
    request_qdict = request.REQUEST

    type = request_qdict.get('type', u'simple')
    if type not in ['simple', 'adv']:
        type = 'simple'

    offset, limit = 0, 20

    c['type'] = type
    debug_params = {
        'limit': limit,
        'offset': offset,
    }

    #perform search
    qs = None
    if type == 'simple':
        query = request_qdict['query']
        debug_params['query'] = query
        finder = SimpleBookFinder(query=query)
        qs = finder.get_as_queryset(limit=limit, offset=offset)

    #format results
    if qs is not None:
        #c['total'] = qs.count()
        c['results'] = qs

        if settings.DEBUG:
            c['debug']['qs_query'] = qs.query.sql
            c['debug']['qs_params'] = pformat(qs.params)

    if settings.DEBUG:
        c['debug']['request_params'] = pformat(debug_params)

    return c