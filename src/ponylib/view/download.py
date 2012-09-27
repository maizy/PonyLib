# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from django.template.loader import render_to_string

__license__         = "GPL3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseNotFound
from django.core.servers.basehttp import FileWrapper
from annoying.decorators import render_to
from django.template import RequestContext

from ponylib.models import Book


@render_to('download/error.html')
def fb2(request, book_id):

    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return _error(request, _('This book doesn\'t exist'))

    if not book.is_file_exists():
        return _error(request, _('Book file "%s" was missing somewhere') % (book.basename))
    file = open(book.full_path, 'r')
    response = HttpResponse(FileWrapper(file), content_type='application/x-fictionbook')
    response['Content-Disposition'] = 'attachment; filename=%s' % book.basename #should not be urlescaped

    return response


def _error(request, error_message):
    c = {
        'page': {
            'title': _('Download'),
        },
        'error_message' : error_message,
    }
    return HttpResponseNotFound(render_to_string('download/error.html', c, RequestContext(request)))