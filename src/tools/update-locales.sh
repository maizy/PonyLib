#!/bin/bash

# License: GPL v3
# Copyright: 2012 maizy.ru"
# Author: Nikita Kovaliov <nikita@maizy.ru>
# Version: 0.1

SCRIPT_PATH=$(cd ${0%/*} && echo $PWD/${0##*/})
PROJECT_ROOT=`dirname "$SCRIPT_PATH"`
PROJECT_ROOT=`dirname "$PROJECT_ROOT"`
PROJECT_ROOT=`dirname "$PROJECT_ROOT"`
WEB_ROOT="$PROJECT_ROOT/src/ponylib"

cd "${WEB_ROOT}"
./../manage.py makemessages -l en_US
./../manage.py makemessages -l ru_RU
./../manage.py compilemessages
