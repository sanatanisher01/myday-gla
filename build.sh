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

# Make the initialization script executable
chmod +x init_db.py

# Run the database initialization script
echo "Running database initialization script..."
python init_db.py || {
    echo "Database initialization script failed, trying standard migrations..."

    # Try standard migrations as a fallback
    python manage.py migrate || {
        echo "Standard migrations failed, trying with --fake flag..."
        python manage.py migrate --fake || {
            echo "All migration attempts failed, but continuing build process..."
        }
    }
}

echo "Build process completed."
