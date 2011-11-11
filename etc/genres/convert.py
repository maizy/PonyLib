#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import os
import sys
import codecs
import re

f = codecs.open('genres.txt', 'r', 'utf-8')

w = codecs.open('initial_data.json', 'w', 'utf-8')

i = 1
reg = re.compile(r'([^\s]+)\s+(.*)')
w.write('[\n')
for line in f:
    line = unicode(line)
    match = reg.match(line)
    print '%s match: "%s" => "%s"' % (i, match.group(1), match.group(2))

    w.write(u"""{
  "model": "ponylib.Genre",
  "pk": %s,
  "fields": {
    "code": "%s",
    "value": "%s",
    "protect": 1
  }
},
""" % (i, match.group(1), match.group(2)))
    i += 1

w.seek(-2, os.SEEK_CUR)
w.write('\n]\n')

w.close()
f.close()