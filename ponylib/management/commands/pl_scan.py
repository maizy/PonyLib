# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2010-2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

import os.path
import sys
import traceback

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
        try:
            for (root_path, file_path) in iter:
                total += 1
                full_path = os.path.join(root_path, file_path)
                self.stdout.write('File: %s\n' % full_path)
                try:
                    mi = meta.read_fb2_meta(full_path)
                    pprint(mi)
                    ok += 1

                except Exception , e: #TODO use my Exceptions
                    parse_errors += 1
                    self.stderr.write('Error in %s, skipping\n' % full_path)
                    self.stderr.write('-'*60+'\n')
                    traceback.print_exc(file=self.stderr)
                    self.stderr.write('-'*60+'\n')

        except KeyboardInterrupt:
            sys.stdout.write('\n')

        sys.stdout.write(("""%d files processed\n\t%d - successful\n\t"""
                         +"""%d - parse errors or broken files\n\t""")
                         % (total, ok, parse_errors))

