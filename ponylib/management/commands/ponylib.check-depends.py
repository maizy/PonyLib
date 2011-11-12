# _*_ coding: utf-8 _*_
from django.core.management.base import BaseCommand, CommandError
#from example.polls.models import Poll
from optparse import make_option

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--do-not-move-files',
            action='store_false',
            dest='move_files',
            default=True,
            help='Move all root files and dirs'),
        )

    args = 'OLD_ROOT_PATH NEW_ROOT_PATH'
    help = u'Move library root'

    def handle(self, *args, **options):
        self.stderr.write('Not realized yet\n\n')