#!/usr/bin/env bash
# Build no Render (ou local): dependências, estáticos, migrações
set -o errexit

pip install -r requirements.txt
python scripts/i18n_audit.py
python scripts/compile_mo.py
python manage.py collectstatic --noinput
python manage.py migrate --noinput
