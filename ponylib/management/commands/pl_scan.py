# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2010-2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

import os.path
import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from upprint import pprint

from ponylib import scanner
from ponylib import meta


class Command(BaseCommand):


    args = '<lib_dir lib_dir ...>'
    help = u'Scan library dirs'


    def handle(self, *args, **options):

        lib_paths = args
        iter = scanner.Iterator(lib_paths)

        self.stdout.write('Scan roots "%s"\n' % '", "'.join(lib_paths))

        total = 0
        ok = 0
        parse_errors = 0
        read_data_errors = 0
        try:
            for (root_path, file_path) in iter:
                total += 1
                full_path = os.path.join(root_path, file_path)
                self.stdout.write('File: %s\n' % full_path)
                try:
                    mi = meta.read_fb2_meta(full_path)

                except Exception, e: #TODO use my Exception
                    parse_errors += 1
                    self.stderr.write('Error in %s, skipping: %r\n' % (full_path, e))

                #pprint(mi, self.stdout)
#                try:
#                    print 'Title: %s' % doc.title()
#                    for author in doc.authors():
#                        print('Author: %s' % author.format())
#                    #print 'Genres: %r' % doc.genres()
#                    #print 'Sequences: %r' % doc.sequences()
#                    for seq in doc.sequences():
#                        print('Sequence: %(name)s (%(number)s)' % seq)
#
#                    print('Annotation: %s' % doc.annotation_text())
#                    ok += 1
#                except meta_old.Exception:
#                    read_data_errors += 1
#                    print('Error in %s, skipping' % full_path)

            sys.stdout.write('\n\n')

        except KeyboardInterrupt:
            sys.stdout.write('\n')
            pass

        sys.stdout.write(("""%d files processed\n\t%d - successful\n\t"""
                         +"""%d - parse errors or broken files\n\t%d - read data errors\n""") 
                         % (total, ok, parse_errors, read_data_errors))

