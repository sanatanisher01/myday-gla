#!/usr/bin/env bash
# exit on error
set -o errexit

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p static media staticfiles

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Database setup
echo "Setting up database..."
python manage.py migrate

# Initialize database with sample data
echo "Initializing database with sample data..."
python manage.py initialize_db

echo "Build process completed."
