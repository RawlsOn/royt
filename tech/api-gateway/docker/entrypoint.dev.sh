#!/bin/sh

# python manage.py flush --no-input
python manage.py migrate
python manage.py migrate geoinfo --database=geoinfo
python manage.py migrate core --database=core
python manage.py collectstatic --no-input
# python manage.py create_base_data

echo "dev loading..."

exec "$@"