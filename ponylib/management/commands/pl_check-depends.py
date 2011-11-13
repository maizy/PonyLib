# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    help = u'Check ponylib depends python and system pkgs'

    def handle(self, *args, **options):
        raise CommandError('Not realized yet')