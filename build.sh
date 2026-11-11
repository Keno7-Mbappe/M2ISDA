#!/usr/bin/env bash
# Script de build exécuté par Render
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py ensure_admin
