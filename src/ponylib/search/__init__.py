# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
__license__         = "GPL3"
__copyright__       = "Copyright 2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

def escape_for_like(val):
    """
    @type val:unicode
    @return:unicode
    """
    val = val.replace('%', r'\%')
    val = val.replace('_', r'\_')

    return val