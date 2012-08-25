# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

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

    offset, limit = 0, 100

    c['type'] = type

    #perform search
    qs = None
    if type == 'simple':
        finder = SimpleBookFinder(query=request_qdict['query'])
        qs = finder.get_as_queryset()

    #format results
    if qs is not None:
        c['total'] = len(qs) #how fast this in django?
        c['results'] = qs[offset:limit]

        if settings.DEBUG:
            c['debug']['results_pformat'] = pformat(c['results'])
            c['debug']['qs_query'] = unicode(qs.query)

    if settings.DEBUG:
        c['debug']['request_params'] = pformat(request_qdict)

    return c