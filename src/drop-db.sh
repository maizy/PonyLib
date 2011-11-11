#!/bin/bash
DROP_SQL=`./manage.py sqlclear ponylib`
DROP_SQL="SET FOREIGN_KEY_CHECKS=0;${DROP_SQL}SET FOREIGN_KEY_CHECKS=1;"
echo "${DROP_SQL}" | mysql --user=ponylib --password=ponylib --database=ponylib
