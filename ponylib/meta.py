# _*_ coding: utf-8 _*_


__license__ = 'GPLv3'
__copyright__ = 'Copyright 2011 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

from datetime import date

from calibre_based import fb2_meta

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
            series['index'] = unicode(res['series_index'], encoding='utf-8')
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

    for fix_string_key in ('publisher', 'language', 'isbn'):
        if fix_string_key in res and \
           res[fix_string_key] is not None and \
           not isinstance(res[fix_string_key], unicode):
            res[fix_string_key] = unicode(res[fix_string_key], encoding='utf-8')

    if 'annotation' in res:
        res['annotation'] = res['annotation'].strip()

    valid_keys = ['authors', 'title', 'language', 'tags', 'series', 'annotation',
                  'isbn', 'publisher', 'pubyear']

    #return {key: res[key] for key in valid_keys} #wait for py2.7
    for key in (set(res.keys()) - set(valid_keys)):
        del res[key]

    return res
