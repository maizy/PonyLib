#!/usr/bin/env python
#special for PyCharm
import os
import os.path as path
import sys

if __name__ == "__main__":

    sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ponylib.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)