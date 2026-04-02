#!/usr/bin/env bash
# Build no Render (ou local): dependências, estáticos, migrações
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
