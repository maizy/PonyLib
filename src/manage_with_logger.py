#!/usr/bin/env python
import os
import sys
import logging

if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ponylib.settings")
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(name)-20s) %(message)s')
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)