#!/bin/bash

# License: GPL v3
# Copyright: 2011 maizy.ru"
# Author: Nikita Kovaliov <nikita@maizy.ru>
# Version: 0.1

# TODO Break for some steps. Db or user may not exist.


SCRIPT_PATH=$(cd ${0%/*} && echo $PWD/${0##*/})
WEB_ROOT="`dirname "$SCRIPT_PATH"`/ponylib"

echo "UNINSTALL"

echo "Are you sure? You've lost everything. [n/Y]"
read areyou

if [ $areyou == "y" -o $areyou == "Y" ]; then

    DROP_SQL=`${WEB_ROOT}/manage.py sqlclear ponylib`

    DROP_SQL="\
    SET FOREIGN_KEY_CHECKS=0;\
    ${DROP_SQL}\
    SET FOREIGN_KEY_CHECKS=1;\
    DROP DATABASE \`ponylib\`;\
    DROP USER 'ponylib'@'localhost';"

    echo "Mysql root user please:"
    echo "${DROP_SQL}" | mysql --user=root --password --database=ponylib


    echo "Done."
else
    echo "Aborted."
fi