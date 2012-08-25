# _*_ coding: utf-8 _*_
__license__         = "GPL3"
__copyright__       = "Copyright 2010-2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

import os.path
import sys
import traceback
import datetime

from django.core.management.base import BaseCommand

from upprint import pprint

from ponylib.models import Root, Series, Author, Book, Genre
from ponylib.models import BookSeries, BookGenre, BookAuthor
from ponylib import scanner, meta


class Command(BaseCommand):


    args = '<lib_dir lib_dir ...>'
    help = u'Scan library dirs'


    def handle(self, *args, **options):

        lib_paths = [os.path.realpath(x) for x in args]

        iter = scanner.Iterator(lib_paths)

        lib_paths_rows = {}
        for lib_path in lib_paths:
            lib_paths_rows[lib_path] = Root.objects.get_by_path_or_create(lib_path)

        self.stdout.write('Scan roots "%s"\n' % '", "'.join(lib_paths))

        total = 0
        ok = 0
        parse_errors = 0
        first = True
        start_time = None
        total_parse_time = 0.0
        total_db_time = 0.0
        total_db_links_time = 0.0

        try:
            for (lib_path, file_path) in iter:
                total += 1

                #ignore iterator warm up
                if first:
                    first = False
                    start_time = datetime.datetime.now()

                try:
                    root = lib_paths_rows[lib_path]
                except KeyError:
                    continue

                full_path = os.path.join(lib_path, file_path)
                self.stdout.write('File: %s\n' % full_path)
                mi = None
                try:
                    before = datetime.datetime.now()
                    mi = meta.read_fb2_meta(full_path)
                    total_parse_time += (datetime.datetime.now() - before).total_seconds()

                    before_db = datetime.datetime.now()
                    #pprint(mi)

                    book = Book()
                    book.root = root
                    book.rel_path=file_path
                    book.title=mi.get('title')
                    if not book.title:
                        #name without ext
                        book.title = os.path.splitext(os.path.basename(file_path))[0]

                    for addit_field in ('title', 'isbn', 'publisher', 'annotation', 'pubyear'):
                        if addit_field in mi and mi[addit_field] is not None:
                            setattr(book, addit_field, mi[addit_field])

                    book.save()

                    before_db_links = datetime.datetime.now()

                    if 'authors' in mi:
                        author_links = []
                        for author_fullname in mi['authors']:
                            author = Author.objects.get_by_fullname_or_create(author_fullname)
                            author_link = BookAuthor()
                            author_link.book = book
                            author_link.author = author
                            author_links.append(author_link)
                        BookAuthor.objects.bulk_create(author_links)

                    if 'genres' in mi:
                        genree_links = []
                        for genree_code in mi['genres']:
                            genree = Genre.objects.get_by_code_or_create(genree_code)
                            genree_link = BookGenre()
                            genree_link.book = book
                            genree_link.genre = genree
                            genree_links.append(genree_link)
                        BookGenre.objects.bulk_create(genree_links)

                    if 'series' in mi:
                        series_links = []
                        for in_series in mi['series']:
                            series = Series.objects.get_by_name_or_create(in_series['name'])
                            series_link = BookSeries()
                            series_link.series = series
                            series_link.book = book
                            if 'index' in in_series:
                                series_link.number = in_series['index']
                        BookSeries.objects.bulk_create(series_links)

                    total_db_links_time += (datetime.datetime.now() - before_db_links).total_seconds()
                    total_db_time += (datetime.datetime.now() - before_db).total_seconds()

                    ok += 1

                except Exception , e: #TODO catch only my Exceptions
                    parse_errors += 1
                    self.stderr.write('Error in %s, skipping\n' % full_path)
                    self.stderr.write('-'*60+'\n')
                    self.stderr.write('Meta info: ')

                    # ignore pprint exceptions here
                    try:
                        pprint(mi, self.stderr)
                    except Exception:
                        self.stderr.write('!Unable to print meta info')

                    self.stderr.write('-'*60+'\n')

                    # ignore traceback exception here
                    try:
                        traceback.print_exc(file=self.stderr)
                    except Exception:
                        self.stderr.write('!Unable to print traceback info')

                    self.stderr.write('-'*60+'\n')

        except KeyboardInterrupt:
            sys.stdout.write('\nUser interrupt\n')

        #count some stat
        stat = ''
        if start_time is not None:
            seconds = (datetime.datetime.now() - start_time).total_seconds()
            if seconds > 0:
                fps = float(total) / seconds
                stat = (u'total time: %(total_time)0.2f sec\n'
                        u'\tmeta data parsing: %(parse_time)0.0f sec (%(parse_percent)0.0f%%)\n'
                        u'\tdb: %(db_time)0.0f sec (%(db_percent)0.0f%%)\n'
                        u'\t\tcreate books: %(db_c_books_time)0.0f sec (%(db_c_books_percent)0.0f%%)\n'
                        u'\t\tcreate books links: %(db_c_links_time)0.0f sec (%(db_c_links_percent)0.0f%%)\n'
                        u'fps: %(fps)0.4f\n') \
                        % {'total_time' : seconds, 'fps': fps,
                           'parse_time' : total_parse_time, 'parse_percent': total_parse_time/seconds*100,
                           'db_time' : total_db_time, 'db_percent': total_db_time/seconds*100,
                           'db_c_links_time' : total_db_links_time, 'db_c_links_percent': total_db_links_time/seconds*100,
                           'db_c_books_time' : (total_db_time-total_db_links_time),
                           'db_c_books_percent': (total_db_time-total_db_links_time)/seconds*100,
                           }

        sys.stdout.write((u'files processed: %d\n'
                          u'\tsuccessful: %d\n'
                          u'\tparse errors or broken files: %d\n'
                          u'%s')
                         % (total, ok, parse_errors, stat))

