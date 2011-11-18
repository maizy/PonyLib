#!/usr/bin/env python
from __future__ import with_statement
__license__   = 'GPL v3'
__copyright__ = '2011, Roman Mukhin <ramses_ru at hotmail.com>, '\
                '2008, Anatoly Shipitsin <norguhtar at gmail.com>'
'''Read meta information from fb2 files'''

import os
import datetime
from functools import partial
from base64 import b64decode
from lxml import etree
from calibre.utils.date import parse_date
from calibre import guess_type, guess_all_extensions, prints, force_unicode
from calibre.ebooks.metadata import MetaInformation, check_isbn
from calibre.ebooks.chardet import xml_to_unicode


NAMESPACES = {
    'fb2'   :   'http://www.gribuser.ru/xml/fictionbook/2.0',
    'xlink' :   'http://www.w3.org/1999/xlink'  }

XPath = partial(etree.XPath, namespaces=NAMESPACES)
tostring = partial(etree.tostring, method='text', encoding=unicode)

def get_metadata(stream):
    ''' Return fb2 metadata as a L{MetaInformation} object '''

    root = _get_fbroot(stream)
    book_title = _parse_book_title(root)
    authors = _parse_authors(root)

    # fallback for book_title
    if book_title:
        book_title = unicode(book_title)
    else:
        book_title = force_unicode(os.path.splitext(
            os.path.basename(getattr(stream, 'name',
                _('Unknown'))))[0])
    mi = MetaInformation(book_title, authors)

    try:
        _parse_cover(root, mi)
    except:
        pass
    try:
        _parse_comments(root, mi)
    except:
        pass
    try:
        _parse_tags(root, mi)
    except:
        pass
    try:
        _parse_series(root, mi)
    except:
        pass
    try:
        _parse_isbn(root, mi)
    except:
        pass
    try:
        _parse_publisher(root, mi)
    except:
        pass
    try:
        _parse_pubdate(root, mi)
    except:
        pass
    try:
        _parse_timestamp(root, mi)
    except:
        pass

    try:
        _parse_language(root, mi)
    except:
        pass
    #_parse_uuid(root, mi)

    #if DEBUG:
    #   prints(mi)
    return mi

def _parse_authors(root):
    authors = []
    # pick up authors but only from 1 secrion <title-info>; otherwise it is not consistent!
    # Those are fallbacks: <src-title-info>, <document-info>
    for author_sec in ['title-info', 'src-title-info', 'document-info']:
        for au in XPath('//fb2:%s/fb2:author'%author_sec)(root):
            author = _parse_author(au)
            if author:
                authors.append(author)
        if author:
            break

    # if no author so far
    if not authors:
        authors.append(_('Unknown'))

    return authors

def _parse_author(elm_author):
    """ Returns a list of display author and sortable author"""

    xp_templ = 'normalize-space(fb2:%s/text())'

    author = XPath(xp_templ % 'first-name')(elm_author)
    lname = XPath(xp_templ % 'last-name')(elm_author)
    mname = XPath(xp_templ % 'middle-name')(elm_author)

    if mname:
        author = (author + ' ' + mname).strip()
    if lname:
        author = (author + ' ' + lname).strip()

    # fallback to nickname
    if not author:
        nname = XPath(xp_templ % 'nickname')(elm_author)
        if nname:
            author = nname

    return author


def _parse_book_title(root):
    # <title-info> has a priority.   (actually <title-info>  is mandatory)
    # other are backup solution (sequence is important. other then in fb2-doc)
    xp_ti = '//fb2:title-info/fb2:book-title/text()'
    xp_pi = '//fb2:publish-info/fb2:book-title/text()'
    xp_si = '//fb2:src-title-info/fb2:book-title/text()'
    book_title = XPath('normalize-space(%s|%s|%s)' % (xp_ti, xp_pi, xp_si))(root)

    return book_title

def _parse_cover(root, mi):
    # pickup from <title-info>, if not exists it fallbacks to <src-title-info>
    imgid = XPath('substring-after(string(//fb2:coverpage/fb2:image/@xlink:href), "#")')(root)
    if imgid:
        try:
            _parse_cover_data(root, imgid, mi)
        except:
            pass

def _parse_cover_data(root, imgid, mi):
    elm_binary = XPath('//fb2:binary[@id="%s"]'%imgid)(root)
    if elm_binary:
        mimetype = elm_binary[0].get('content-type', 'image/jpeg')
        mime_extensions = guess_all_extensions(mimetype)

        if not mime_extensions and mimetype.startswith('image/'):
            mimetype_fromid = guess_type(imgid)[0]
            if mimetype_fromid and mimetype_fromid.startswith('image/'):
                mime_extensions = guess_all_extensions(mimetype_fromid)

        if mime_extensions:
            pic_data = elm_binary[0].text
            if pic_data:
                mi.cover_data = (mime_extensions[0][1:], b64decode(pic_data))
        else:
            prints("WARNING: Unsupported coverpage mime-type '%s' (id=#%s)" % (mimetype, imgid) )

def _parse_tags(root, mi):
    # pick up genre but only from 1 secrion <title-info>; otherwise it is not consistent!
    # Those are fallbacks: <src-title-info>
    for genre_sec in ['title-info', 'src-title-info']:
        # -- i18n Translations-- ?
        tags = XPath('//fb2:%s/fb2:genre/text()' % genre_sec)(root)
        if tags:
            mi.tags = list(map(unicode, tags))
            break

def _parse_series(root, mi):
    # calibri supports only 1 series: use the 1-st one
    # pick up sequence but only from 1 secrion in prefered order
    # except <src-title-info>
    xp_ti = '//fb2:title-info/fb2:sequence[1]'
    xp_pi = '//fb2:publish-info/fb2:sequence[1]'

    elms_sequence = XPath('%s|%s' % (xp_ti, xp_pi))(root)
    if elms_sequence:
        mi.series = elms_sequence[0].get('name', None)
        if mi.series:
            mi.series_index = elms_sequence[0].get('number', None)

def _parse_isbn(root, mi):
    # some people try to put several isbn in this field, but it is not allowed.  try to stick to the 1-st one in this case
    isbn = XPath('normalize-space(//fb2:publish-info/fb2:isbn/text())')(root)
    if isbn:
        # some people try to put several isbn in this field, but it is not allowed.  try to stick to the 1-st one in this case
        if ',' in isbn:
            isbn = isbn[:isbn.index(',')]
        if check_isbn(isbn):
            mi.isbn = isbn

def _parse_comments(root, mi):
    # pick up annotation but only from 1 secrion <title-info>;  fallback: <src-title-info>
    for annotation_sec in ['title-info', 'src-title-info']:
        elms_annotation = XPath('//fb2:%s/fb2:annotation' % annotation_sec)(root)
        if elms_annotation:
            mi.comments = tostring(elms_annotation[0])
            # TODO: tags i18n, xslt?
            break

def _parse_publisher(root, mi):
    publisher = XPath('string(//fb2:publish-info/fb2:publisher/text())')(root)
    if publisher:
        mi.publisher = publisher

def _parse_pubdate(root, mi):
    year = XPath('number(//fb2:publish-info/fb2:year/text())')(root)
    if float.is_integer(year):
        # only year is available, so use 1-st of Jan
        mi.pubdate = datetime.date(int(year), 1, 1)

def _parse_timestamp(root, mi):
    #<date value="1996-12-03">03.12.1996</date>
    xp ='//fb2:document-info/fb2:date/@value|'\
        '//fb2:document-info/fb2:date/text()'
    docdate = XPath('string(%s)' % xp)(root)
    if docdate:
        mi.timestamp = parse_date(docdate)

def _parse_language(root, mi):
    language = XPath('string(//fb2:title-info/fb2:lang/text())')(root)
    if language:
        mi.language = language
        mi.languages = [ language ]

def _parse_uuid(root, mi):
    uuid = XPath('normalize-space(//document-info/fb2:id/text())')(root)
    if uuid:
        mi.uuid = uuid

def _get_fbroot(stream):
    parser = etree.XMLParser(recover=True, no_network=True)
    raw = stream.read()
    raw = xml_to_unicode(raw, strip_encoding_pats=True)[0]
    root = etree.fromstring(raw, parser=parser)
    return root
