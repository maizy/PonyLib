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
                    mi = meta.read_fb2_meta(full_path)

                    #pprint(mi)

                    book = Book()
                    book.root = root
                    book.rel_path=file_path
                    book.title=mi['title']

                    for addit_field in ('title', 'isbn', 'publisher', 'annotation', 'pubyear'):
                        if addit_field in mi and mi[addit_field] is not None:
                            setattr(book, addit_field, mi[addit_field])

                    book.save()

                    if 'authors' in mi:
                        for author_fullname in mi['authors']:
                            author = Author.objects.get_by_fullname_or_create(author_fullname)
                            author_link = BookAuthor()
                            author_link.book = book
                            author_link.author = author
                            author_link.save()

                    if 'genres' in mi:
                        for genree_code in mi['genres']:
                            genree = Genre.objects.get_by_code_or_create(genree_code)
                            genree_link = BookGenre()
                            genree_link.book = book
                            genree_link.genre = genree
                            genree_link.save()

                    if 'series' in mi:
                        for in_series in mi['series']:
                            series = Series.objects.get_by_name_or_create(in_series['name'])
                            series_link = BookSeries()
                            series_link.series = series
                            series_link.book = book
                            if 'index' in in_series:
                                series_link.number = in_series['index']
                            series_link.save()


                    ok += 1

                except Exception , e: #TODO catch only my Exceptions
                    parse_errors += 1
                    self.stderr.write('Error in %s, skipping\n' % full_path)
                    self.stderr.write('-'*60+'\n')
                    self.stderr.write('Meta info: ')
                    pprint(mi, self.stderr)
                    self.stderr.write('-'*60+'\n')
                    traceback.print_exc(file=self.stderr)
                    self.stderr.write('-'*60+'\n')

        except KeyboardInterrupt:
            sys.stdout.write('\nUser interrupt\n')

        #count some stat
        stat = ''
        if start_time is not None:
            seconds = (datetime.datetime.now() - start_time).total_seconds()
            if seconds > 0:
                fps = float(total) / seconds
                stat = u'scan time: %0.0f sec (%0.4f fps)\n' \
                        % (seconds, fps)

        sys.stdout.write((u'files processed: %d\n'
                          u'\tsuccessful: %d\n'
                          u'\tparse errors or broken files: %d\n'
                          u'%s')
                         % (total, ok, parse_errors, stat))

