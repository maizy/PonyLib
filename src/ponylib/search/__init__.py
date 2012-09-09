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

def get_db_type():
    try:
        from django.db import backend
        name = backend.__name__
        if 'mysql' in name:
            return 'mysql'

        if 'postgresql' in name:
            return 'postgre'

        if 'sqlite' in name:
            return 'sqlite'
    except ImportError:
        pass

    return None

def is_supported_db():

    db = get_db_type()
    return db is not None

def is_sqlite():
    return get_db_type() == 'sqlite'

def is_postgre():
    return get_db_type() == 'postgre'

def is_mysql():
    return get_db_type() == 'postgre'