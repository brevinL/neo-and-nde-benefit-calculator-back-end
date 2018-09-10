#!/bin/sh
set -e

chmod 740 /root/.mylogin.cnf
until mysqladmin --defaults-file=/root/.mylogin.cnf ping --silent; do 
  >&2 echo "Database is unavailable - sleeping"
  sleep 1
done

>&2 echo "Database is up - continuing"

python manage.py makemigrations
python manage.py migrate
python populate_benefit_rules.py

exec "$@"
