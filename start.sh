#!/usr/bin/env bash
set -e

python manage.py migrate --noinput
gunicorn tu_canasta_backend.wsgi:application
