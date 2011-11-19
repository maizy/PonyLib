#!/bin/bash

# License: GPL v3
# Copyright: 2011 maizy.ru"
# Author: Nikita Kovaliov <nikita@maizy.ru>
# Version: 0.1

# TODO: ask for user, pass, db ...
# TODO: auto write django configs

SCRIPT_PATH=$(cd ${0%/*} && echo $PWD/${0##*/})
WEB_ROOT="`dirname "$SCRIPT_PATH"`/ponylib"


echo '* Add mysql database and user'

INIT_SQL=$( cat <<SQL
CREATE DATABASE \`ponylib\` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER 'ponylib'@'localhost' IDENTIFIED BY 'ponylib';
GRANT USAGE ON * . * TO  'ponylib'@'localhost'
    IDENTIFIED BY  'ponylib'
    WITH MAX_QUERIES_PER_HOUR 0
    MAX_CONNECTIONS_PER_HOUR 0
    MAX_UPDATES_PER_HOUR 0
    MAX_USER_CONNECTIONS 0 ;
GRANT ALL PRIVILEGES ON  \`ponylib\` . * TO  'ponylib'@'localhost';
SQL
)

echo '> Mysql root password, please:'
echo "${INIT_SQL}"| mysql --user=root --password

if [ $? -eq 0 ];then
    echo '* Db created'
else
    echo "! Something went wrong :( - mysql return code ${?}"
    exit 1
fi

#TODO south
echo '* Create south databases'
$WEB_ROOT/manage.py syncdb
echo '* Load init migrations'
$WEB_ROOT/manage.py migrate ponylib

echo '* Done'