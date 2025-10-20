#!/usr/bin/env bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn tu_canasta_backend.wsgi:application
