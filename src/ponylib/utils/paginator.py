# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'MIT'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

from itertools import repeat
from types import MethodType

from django.core.paginator import Paginator, Page, PageNotAnInteger, EmptyPage

class SimplePaginator(Paginator):

    def __init__(self, count, per_page, orphans=0, allow_empty_first_page=True):
        dump_list = list(repeat(None, count))
        super(SimplePaginator, self).__init__(
            dump_list, per_page=per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page)


class LimitOffsetPaginator(Paginator):

    def get_limit(self):
        return self.per_page

    def page(self, number):
        #dinamically extend page instance
        page = super(LimitOffsetPaginator, self).page(number)
        page.get_offset = MethodType(lambda page: self.get_offset(page), page)
        return page

    def get_offset(self, page):
        if not isinstance(page, Page):
            page = self.page(page)
        index = page.start_index()
        if index > 0:
            index -= 1
        return index

class SimpleLimitOffsetPaginator(SimplePaginator, LimitOffsetPaginator):
    pass


def build_pseudo_paginator(count, per_page, page=None):
    paginator = SimpleLimitOffsetPaginator(count, per_page)
    try:
        page = paginator.page(page)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage: #over last page
        page = paginator.page(paginator.num_pages)

    return page, paginator