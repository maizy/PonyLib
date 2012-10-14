# _*_ coding: utf-8 _*_


__license__ = 'GPLv3'
__copyright__ = 'Copyright 2011 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

from datetime import date

from calibre_based import fb2_meta
from django.utils.encoding import force_unicode as django_force_unicode

def force_unicode(*args, **kwargs):
    res = django_force_unicode(*args, **kwargs)

    #django not fix some "not_real_unicode" like lxml.etree._ElementUnicodeResult
    #witch is bad for mysqlDb
    if res.__class__ is not unicode:
        res = unicode(res)

    return res

class ConvertError(Exception):
    pass

def read_fb2_meta(filepath):
    """
    Read fb2 meta information


    @rtype: dict
    @return: {
                 'authors': [unicode, ...],
                 'title': unicode,
                 'language': unicode, #iso639-1
                 'genres': [unicode, ...],
                 'series': [{'name': unicode, 'index': unicode|None}, ...],
                 'annotation': unicode,
                 'isbn': unicode,
                 'publisher': unicode,
                 'pubyear': int|None,
             }
    """

    with open(filepath, 'r') as stream:
        mi = fb2_meta.get_metadata(stream)

    calibre_meta = mi.__dict__

    meta = {}

    #using force_unicode for all values, becouse of bad lxml unicode instancies

    # authors
    if 'authors' in calibre_meta:
        meta['authors'] = map(force_unicode, calibre_meta['authors'])

    # simple fields
    for (calibre_prop, meta_key) in [
            ('comments', 'annotation'),
            ('book_title', 'title'),
            ('language', 'language'),
            ('isbn', 'isbn'),
            ('publisher', 'publisher'),
        ]:
        if calibre_prop in calibre_meta and calibre_meta[calibre_prop] is not None:
            meta[meta_key] = force_unicode(calibre_meta[calibre_prop])


    if 'annotation' in meta:
        meta['annotation'] = meta['annotation'].strip()

    #series
    if 'series' in calibre_meta:

        series = {
            'name': force_unicode(calibre_meta['series'])
        }

        if 'series_index' in calibre_meta and calibre_meta['series_index'] is not None:
            series['index'] = force_unicode(calibre_meta['series_index'])

        meta['series'] = [series]

    #pubyear
    if 'pubdate' in calibre_meta and isinstance(calibre_meta['pubdate'], date):
        meta['pubyear'] = calibre_meta['pubdate'].year

    #genres
    if 'tags' in calibre_meta:
        meta['genres'] = map(force_unicode, calibre_meta['tags'])

    return meta