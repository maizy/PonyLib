# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2010-2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    args = 'OLD_ROOT_PATH NEW_ROOT_PATH'
    help = 'Move library root'

    def handle(self, *args, **options):
        raise CommandError('Not realized yet')