#!/usr/bin/env bash
# exit on error
set -o errexit

# Print environment variables for debugging
echo "Environment variables:"
echo "DATABASE_URL exists: $(if [ -n "$DATABASE_URL" ]; then echo "Yes"; else echo "No"; fi)"
echo "RAILWAY_ENVIRONMENT: $RAILWAY_ENVIRONMENT"

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

    # Run migrations with fake-initial to avoid CASCADE issues
    echo "Running migrations with fake-initial..."
    python manage.py migrate --fake-initial

    # Run setup_railway command
    echo "Running setup_railway command..."
    python manage.py setup_railway

    # Initialize database with sample data
    echo "Initializing database with sample data..."
    python manage.py initialize_db
else
    echo "DATABASE_URL is not set, using SQLite database..."
    python manage.py migrate --fake-initial
    python manage.py setup_railway
    python manage.py initialize_db
fi

echo "Build process completed."
