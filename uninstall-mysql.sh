#!/bin/bash

SCRIPT_PATH=$(cd ${0%/*} && echo $PWD/${0##*/})
WEB_ROOT="`dirname "$SCRIPT_PATH"`/ponylib"

DROP_SQL=`${WEB_ROOT}/manage.py sqlclear ponylib`
DROP_SQL="SET FOREIGN_KEY_CHECKS=0;${DROP_SQL}SET FOREIGN_KEY_CHECKS=1;"
echo "${DROP_SQL}" | mysql --user=ponylib --password=ponylib --database=ponylib
