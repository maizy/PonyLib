#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import os
import sys
import codecs
import re

f = codecs.open('genres.txt', 'r', 'utf-8')

w = codecs.open('genres.json', 'w', 'utf-8')

i = 1
reg = re.compile(r'([^\s]+)\s+(.*)')
w.write('[\n')
for line in f:
    line = unicode(line)
    match = reg.match(line)
    print '%s match: "%s" => "%s"' % (i, match.group(1), match.group(2))

    code = match.group(1)
    value_ru = match.group(2)
    value_en = ' '.join([word[0].capitalize() + word[1:] for word in code.split('_')])

    w.write(u"""{
  "model": "ponylib.Genre",
  "pk": %s,
  "fields": {
    "code": "%s",
    "value_ru": "%s",
    "value_en": "%s",
    "protect": 1
  }
},
""" % (i, code, value_ru, value_en))
    i += 1

w.seek(-2, os.SEEK_CUR)
w.write('\n]\n')

w.close()
f.close()