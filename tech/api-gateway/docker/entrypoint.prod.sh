#!/bin/bash

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# python manage.py flush --no-input
python manage.py migrate
# python manage.py collectstatic --no-input

# echo "wait for juso-ms..."
# while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' juso-ms/apt-list?search=whatever)" != "200" ]]; do
#     printf '.';
#     sleep 2;
# done

echo "prod loading..."

gunicorn ms_skeleton.wsgi:application --bind 0.0.0.0:8000 --limit-request-line 0