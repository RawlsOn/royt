#!/bin/bash

# python manage.py flush --no-input
# python manage.py migrate
# python manage.py collectstatic --no-input
# python manage.py create_base_data

# echo "wait for juso-ms..."
# while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' juso-ms/apt-list?search=whatever)" != "200" ]]; do
#     printf '.';
#     sleep 2;
# done

echo "staging loading..."

python manage.py migrate
python manage.py migrate
python manage.py migrate geoinfo --database=geoinfo

date

gunicorn ms_skeleton.wsgi:application --bind 0.0.0.0:8000 --limit-request-line 0