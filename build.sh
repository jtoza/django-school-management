#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Attempt to migrate — skip if already applied
python manage.py migrate --noinput || echo "Migration failed or already applied, continuing build..."

# Load your data
python manage.py loaddata data.json || echo "Skipping data load if already exists"
