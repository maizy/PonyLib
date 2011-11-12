#!/bin/bash

SCRIPT_PATH=$(cd ${0%/*} && echo $PWD/${0##*/})
WEB_ROOT="`dirname "$SCRIPT_PATH"`/ponylib"

#TODO Break for some steps. Db or user may not exist.

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