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

    stream = file(filepath, 'r')
    mi = fb2_meta.get_metadata(stream)
    stream.close()
    res = mi.__dict__

    if 'series' in res:
        series = {'name': res['series']}
        if 'series_index' in res and res['series_index'] is not None:
            series['index'] = force_unicode(res['series_index'])
        res['series'] = [series]

    if 'pubdate' in res and isinstance(res['pubdate'], date):
        res['pubyear'] = res['pubdate'].year

    for (calibre_prop, our_key) in [
            ('comments', 'annotation'),
            ('book_title', 'title'),
            ('tags', 'genres'),
        ]:
        if calibre_prop in res:
            res[our_key] = res[calibre_prop]
            del res[calibre_prop]

    for fix_string_key in ('title', 'language', 'annotation',
                           'isbn', 'publisher'):
        if fix_string_key in res and \
           res[fix_string_key] is not None and \
           res[fix_string_key].__class__ is not unicode: #only real_unicode, not unicode extends
            res[fix_string_key] = force_unicode(res[fix_string_key])

    if 'annotation' in res:
        res['annotation'] = res['annotation'].strip()

    valid_keys = ['authors', 'title', 'language', 'genres', 'series', 'annotation',
                  'isbn', 'publisher', 'pubyear']

    #return {key: res[key] for key in valid_keys} #wait for py2.7
    for key in (set(res.keys()) - set(valid_keys)):
        del res[key]

    return res
