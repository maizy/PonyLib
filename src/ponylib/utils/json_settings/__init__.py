# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = ''
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'
__doc__ = ''

import json
import minify_json

# little hack. var dynamically set at ponylib.settings
settings_path = None


def parse_json_with_comments(path):
    """
    Stript comment and parse json

    Based on solution from Damien Riquet:
    http://www.lifl.fr/~riquetd/parse-a-json-file-with-comments.html
    """
    with open(path, 'r') as file:
        content = file.read().decode('utf-8')
        content = minify_json.json_minify(content)

    return json.loads(content)

