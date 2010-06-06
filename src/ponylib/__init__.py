# _*_ coding: utf-8 _*_

import sys
import os

PONYLIB_DIR = os.path.basename(__file__)
LIBS_DIR = os.path.relpath(os.path.join(PONYLIB_DIR, '..', 'libs'))

if LIBS_DIR not in sys.path:
    sys.path.append(LIBS_DIR)