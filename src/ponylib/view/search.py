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
import ponylib.search.errors as search_errors

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
        'disable_quick_search' : True,
        'debug_query' : False,
        'debug_query_data' : {},
    }

    #use post, than get
    request_qdict = request.REQUEST

    debug_query = request.GET.get('debug_query') == '1' and settings.DEBUG

    type = request_qdict.get('type', u'simple')
    if type not in ['simple', 'adv']:
        type = 'simple'
    c['type'] = type

    offset, limit = 0, 20

    debug_params = {
        'limit': limit,
        'offset': offset,
    }

    #perform search
    qs = None
    try:
        if type == 'simple':
            query = request_qdict['query']
            debug_params['query'] = query
            c['query'] = query

            finder = SimpleBookFinder(query=query)
            qs = finder.get_as_queryset(limit=limit, offset=offset)
    except search_errors.SearchError, e:
        c['has_search_errors'] = True
        c['search_errors'] = [_(e.user_message)]



    #format results
    if qs is not None:
        c['results'] = qs

        if debug_query:
            c['debug_query_data']['qs_query'] = qs.query.sql
            c['debug_query_data']['qs_params'] = pformat(qs.params)

    if debug_query:
        c['debug_query'] = True
        c['debug_query_data']['request_params'] = pformat(debug_params)

    return c