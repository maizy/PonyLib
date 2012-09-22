# _*_ coding: utf-8 _*_


__author__ = u'Леонид Швечиков, Nikita Kovaliov'
# http://softwaremaniacs.org/forum/python/25696/

import sys
from pprint import PrettyPrinter

class MyPrettyPrinter(PrettyPrinter):
    def format(self, *args, **kwargs):
        repr, readable, recursive = PrettyPrinter.format(self, *args, **kwargs)
        if repr:
            if repr[0] in ('"', "'"):
                repr = repr.decode('string_escape')
            elif repr[0:2] in ("u'", 'u"'):
                enc = sys.stdout.encoding and sys.stdout.encoding or 'UTF-8'
                repr = repr.decode('unicode_escape').encode(enc)
        return repr, readable, recursive

def pprint(obj, stream=None, indent=1, width=80, depth=None):
    printer = MyPrettyPrinter(stream=stream, indent=indent, width=width, depth=depth)
    printer.pprint(obj)

def pformat(object, indent=1, width=80, depth=None):
    """Format a Python object into a pretty-printed representation."""
    return MyPrettyPrinter(indent=indent, width=width, depth=depth).pformat(object)