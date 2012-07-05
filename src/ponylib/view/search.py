# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

from annoying.decorators import render_to

@render_to('search/search_form.html')
def index(request):

    c = {
        'page': {
            'title': 'Search',
        }
    }

    return c

@render_to('search/results.html')
def results(request):

    c = {
        'page': {
            'title': 'Search Results',
        }
    }

    return c