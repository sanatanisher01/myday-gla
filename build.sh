#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations only if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "Database URL is set, running migrations..."
    python manage.py migrate
else
    echo "Database URL is not set, skipping migrations..."
fi
