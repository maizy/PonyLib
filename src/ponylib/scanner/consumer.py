# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPL v3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

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

        for (root_path, rel_path) in self.queue_iter(files_queue):
            self.logger.debug('%s/%s' % (root_path, rel_path))
            full_path = path.join(root_path, rel_path)

            #TODO lru cache
            root = Root.objects.get_by_path_or_create(root_path, using=alias)
            root_id = root.id

            book = Book()
            book.root_id = root_id
            book.rel_path = rel_path

            try:
                meta_data = self._read_meta_data(full_path)
            except Exception: #TODO: add special parsing exception
                meta_data = {}
                book.has_index_errors = True

            book.title=meta_data.get('title')
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
                    author = Author.objects.get_by_fullname_or_create(author_fullname)
                    author_id = author.id

                    author_link = BookAuthor()
                    author_link.book = book
                    author_link.author_id = author_id
                    author_links.append(author_link)
                BookAuthor.objects.using(alias).bulk_create(author_links)

            if 'genres' in meta_data:
                genree_links = []
                for genree_code in meta_data['genres']:
                    #TODO lru cache
                    genree = Genre.objects.get_by_code_or_create(genree_code)
                    genree_id = genree.id

                    genree_link = BookGenre()
                    genree_link.book = book
                    genree_link.genre_id = genree_id
                    genree_links.append(genree_link)
                BookGenre.objects.using(alias).bulk_create(genree_links)

            if 'series' in meta_data:
                series_links = []
                for in_series in meta_data['series']:
                    #TODO lru cache
                    series = Series.objects.get_by_name_or_create(in_series['name'])
                    series_id = series.id

                    series_link = BookSeries()
                    series_link.series_id = series_id
                    series_link.book = book
                    if 'index' in in_series:
                        series_link.number = in_series['index']
                    series_links.append(series_link)
                BookSeries.objects.using(alias).bulk_create(series_links)

            book.update_search_index()

            print('.')


    def _read_meta_data(self, full_path):
        return read_fb2_meta(full_path)







