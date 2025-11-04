#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Try to apply migrations, but don’t stop if there’s a harmless failure
python manage.py migrate --noinput || echo "Migration failed, continuing build..."
