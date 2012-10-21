# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPL v3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

import sys
import os.path as path

from ponylib.models import \
    Root, Series, Author, Book, Genre, BookSeries, BookGenre, BookAuthor
from ponylib.meta import read_fb2_meta
from ponylib.utils.pool import Consumer


class AddOrUpdateBookConsumer(Consumer):


    logger_name = 'ponylib.scanner'
    #TODO update logic
    allow_update = False


    def consume(self):

        files_queue = self.kwargs['files_queue']
        alias = self.kwargs['connection_alias']
        stat = self.kwargs.get('stat')

        for (root_path, rel_path) in self.queue_iter(files_queue):
            self._process_path(root_path, rel_path,
                alias=alias, stat=stat)

    def _process_path(self, root_path, rel_path, alias=None, stat=None):
        self.logger.debug('%s/%s' % (root_path, rel_path))
        full_path = path.join(root_path, rel_path)

        get_root_timer = None
        meta_data_timer = None
        add_book_timer = None

        if stat is not None:
            get_root_timer = stat.timer('consumer.process_path[get root]')

        root_id = Root.objects.get_id_by_path_or_create(root_path, using=alias)

        if stat is not None:
            get_root_timer()
            meta_data_timer = stat.timer('consumer.process_path[parse meta data]')

        meta_data, has_index_errors = self._read_meta_data(full_path)

        if stat is not None:
            meta_data_timer()
            add_book_timer = stat.timer('consumer.process_path[add book]')

        self._add_book(root_id, rel_path, meta_data,
            has_index_errors=has_index_errors, alias=alias)

        if stat is not None:
            add_book_timer()
            stat.add_book_stat()

    def _read_meta_data(self, full_path):
        has_index_errors = False
        try:
            meta = read_fb2_meta(full_path)
        except Exception: #TODO concrete Exceptions class
            meta = {}
            has_index_errors = True
        return meta, has_index_errors

    def _add_book(self, root_id, rel_path, meta_data, has_index_errors=False, alias=None):
        book = Book()
        book.root_id = root_id
        book.rel_path = rel_path
        book.has_index_errors = has_index_errors
        book.title = meta_data.get('title')
        if not book.title:
            #name without ext
            book.title = path.splitext(path.basename(rel_path))[0]
        for addit_field in ('title', 'isbn', 'publisher', 'annotation', 'pubyear'):
            val = meta_data.get(addit_field)
            if val is not None:
                setattr(book, addit_field, val)
        book.save(using=alias)
        if 'authors' in meta_data:
            author_links = []
            for author_fullname in meta_data['authors']:
                #TODO lru cache
                author_id = Author.objects.get_id_by_fullname_or_create(author_fullname)

                author_link = BookAuthor()
                author_link.book = book
                author_link.author_id = author_id
                author_links.append(author_link)
            BookAuthor.objects.using(alias).bulk_create(author_links)
        if 'genres' in meta_data:
            genree_links = []
            for genree_code in meta_data['genres']:
                #TODO lru cache
                genree_id = Genre.objects.get_id_by_code_or_create(genree_code)

                genree_link = BookGenre()
                genree_link.book = book
                genree_link.genre_id = genree_id
                genree_links.append(genree_link)
            BookGenre.objects.using(alias).bulk_create(genree_links)
        if 'series' in meta_data:
            series_links = []
            for in_series in meta_data['series']:
                #TODO lru cache
                series_id = Series.objects.get_id_by_name_or_create(in_series['name'])

                series_link = BookSeries()
                series_link.series_id = series_id
                series_link.book = book
                if 'index' in in_series:
                    series_link.number = in_series['index']
                series_links.append(series_link)
            BookSeries.objects.using(alias).bulk_create(series_links)
        book.update_search_index()








