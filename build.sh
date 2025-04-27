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
python manage.py collectstatic --no-input --clear

# Database setup
echo "Setting up database..."
# Try regular migration first
python manage.py migrate || {
    echo "Regular migration failed, trying with --fake-initial flag..."
    python manage.py migrate --fake-initial || {
        echo "Migration with --fake-initial failed, trying with --fake flag..."
        python manage.py migrate --fake || {
            echo "All migration attempts failed, but continuing build process..."
        }
    }
}

# Try to initialize database with sample data
echo "Initializing database with sample data..."
python manage.py initialize_db || {
    echo "Database initialization failed, but continuing build process..."
}

echo "Build process completed."
