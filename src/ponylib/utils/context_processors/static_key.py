# _*_ coding: utf-8 _*_


__license__         = "GPL3"
__copyright__       = "Copyright 2012 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

from django.conf import settings
def static_key(request):
    """
    @type request: django.http.HttpRequest

    """

    return {
        'STATIC_KEY' : settings.STATIC_KEY
    }