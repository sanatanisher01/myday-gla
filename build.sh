#!/usr/bin/env bash
# exit on error
set -o errexit

# Print environment variables for debugging
echo "Environment variables:"
echo "DATABASE_URL: $DATABASE_URL"
echo "RENDER: $RENDER"

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p static media staticfiles

# Install dependencies
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input || {
    echo "Static file collection failed, but continuing..."
}

# Database setup
echo "Setting up database..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 15

# Try to run migrations, but continue if they fail
echo "Running migrations..."
python manage.py migrate --noinput || {
    echo "Migrations failed, but continuing with deployment..."
}

# Try to initialize database with sample data
echo "Initializing database with sample data..."
python manage.py initialize_db || {
    echo "Database initialization failed, but continuing with deployment..."
}

echo "Build process completed."
