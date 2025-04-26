#!/usr/bin/env bash
# exit on error
set -o errexit

# Print environment variables for debugging
echo "Environment variables:"
echo "DATABASE_URL exists: $(if [ -n "$DATABASE_URL" ]; then echo "Yes"; else echo "No"; fi)"
echo "RENDER: $RENDER"

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p static media staticfiles

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input || {
    echo "Static file collection failed, but continuing..."
}

# Database setup
echo "Setting up database..."

# Check if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "DATABASE_URL is set, proceeding with PostgreSQL setup..."

    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        echo "Attempt $i: Testing database connection..."
        if python -c "
import sys
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    conn.close()
    print('Database connection successful')
    sys.exit(0)
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
" ; then
            echo "Database is ready!"
            break
        else
            echo "Database not ready yet, waiting..."
            sleep 5
        fi

        if [ $i -eq 30 ]; then
            echo "Database connection timed out after 30 attempts, but continuing..."
        fi
    done

    # Try to run migrations
    echo "Running migrations..."
    python manage.py migrate --noinput || {
        echo "Migrations failed, but continuing with deployment..."
    }

    # Try to initialize database with sample data
    echo "Initializing database with sample data..."
    python manage.py initialize_db || {
        echo "Database initialization failed, but continuing with deployment..."
    }
else
    echo "DATABASE_URL is not set, skipping database setup..."
fi

echo "Build process completed."
