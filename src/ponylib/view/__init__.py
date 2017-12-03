# _*_ coding: utf-8 _*_
__license__ = 'GPL v3'
__copyright__ = 'Copyright 2011 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

from django.conf import settings
from django.shortcuts import redirect
import base64

SIMPLE_PASSWORD_COOKIE_NAME = 'simple_password'


def check_password(request):
    if settings.SIMPLE_PASSWORD:
        cookie = request.get_signed_cookie(SIMPLE_PASSWORD_COOKIE_NAME, None)
        if cookie is None or base64.b64decode(cookie) != settings.SIMPLE_PASSWORD:
            return redirect("/auth")
    return None


def set_password(password):
    if settings.SIMPLE_PASSWORD:
        if settings.SIMPLE_PASSWORD != password:
            return {'wrong_password': True}
        response = redirect("/")
        # N.B. base64 encode is not crypting, but it the same as in HTTP basic auth
        response.set_signed_cookie(SIMPLE_PASSWORD_COOKIE_NAME, value=base64.b64encode(password),
                                   max_age=60*60*24*14, httponly=True)
        return response
    return {}
