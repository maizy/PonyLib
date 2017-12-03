# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__         = "GPL3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

from annoying.decorators import render_to
from django.utils.translation import ugettext as _
from django.conf import settings
from django.shortcuts import redirect

from ponylib.search.simple import get_simple_finder_class
from ponylib.search.errors import SearchError
from ponylib.utils.paginator import build_pseudo_paginator
from ponylib.search import engines
from ponylib.view import check_password

@render_to('search/search_form.html')
def index(request):
    check_res = check_password(request)
    if check_res is not None:
        return check_res
    c = {
        'page': {
            'title': _('Search'),
        },
        'disable_quick_search' : True,
    }

    return c


@render_to('search/results.html')
def results(request):
    check_res = check_password(request)
    if check_res is not None:
        return check_res
    c = {
        'page': {
            'title': _('Search Results'),
        },
        'disable_quick_search' : True,
        'debug_query' : False,
        'debug_query_data' : {},
        'query': '',
        'results_offset': 0,
        'results_limit': None,
    }

    debug_query = ( settings.DEBUG and request.GET.get('debug_query') == '1' )
    c['debug_query'] = debug_query

    type = request.REQUEST.get('type', u'simple')
    if type not in ['simple', 'adv']:
        type = 'simple'
    c['type'] = type

    paginator = None
    paginator_page = None
    results = None
    per_page = 10
    try:
        #perform search
        if type == 'simple':
            query = request.REQUEST.get('query')

            if query is None or len(query) == 0:
                return redirect('search')

            c['query'] = query
            finder_class = get_simple_finder_class()
            finder = finder_class(query=query)
            finder.engine = engines.engine
            paginator_page, paginator = build_pseudo_paginator(finder.count(), per_page, request.REQUEST.get('page'))

            results = finder.build_queryset(paginator.per_page, paginator_page.get_offset())

    except SearchError, e:
        #search errors
        c['has_search_errors'] = True
        c['search_errors'] = [_(e.user_message)]


    #pagination
    if results is not None:


        c['results'] = results
        c['paginator'] = paginator
        c['paginator_page'] = paginator_page

        c['total_count'] = paginator.count
        c['results_offset'] = paginator_page.get_offset()
        c['results_limit'] = paginator.per_page

#        if debug_query:
#            c['debug_query_data']['qs_query'] = qs.query.sql
#            c['debug_query_data']['qs_params'] = pformat(qs.params)

    return c
