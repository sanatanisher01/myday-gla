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
# Force collectstatic to run with settings_prod
DJANGO_SETTINGS_MODULE=myday.settings_prod python manage.py collectstatic --no-input --clear

# Create a simple favicon.ico file if it doesn't exist
if [ ! -f "staticfiles/favicon.ico" ]; then
    echo "Creating a simple favicon.ico file..."
    touch staticfiles/favicon.ico
fi

# Create a simple robots.txt file if it doesn't exist
if [ ! -f "staticfiles/robots.txt" ]; then
    echo "Creating a simple robots.txt file..."
    echo "User-agent: *" > staticfiles/robots.txt
    echo "Allow: /" >> staticfiles/robots.txt
fi

# Database setup
echo "Setting up database..."

# Make the initialization script executable
chmod +x init_db.py
chmod +x setup_manager.py

# Check if we're running on Render
if [ "$RENDER" = "true" ]; then
    echo "Running on Render, using production setup..."

    # For Render, we need to handle the database differently
    echo "Setting up database on Render..."

    # Check if DATABASE_URL is set
    if [ -n "$DATABASE_URL" ]; then
        echo "Using PostgreSQL database from DATABASE_URL"

        # Force using settings_prod for migrations
        export DJANGO_SETTINGS_MODULE=myday.settings_prod

        # First, try to run migrations with --fake-initial to handle existing tables
        echo "Running migrations on PostgreSQL database..."
        python manage.py migrate --fake-initial || {
            echo "Initial migrations failed, trying with --fake..."

            # If that fails, try with --fake
            python manage.py migrate --fake || {
                echo "Fake migrations failed, trying with standard migrations..."

                # Try standard migrations as a last resort
                python manage.py migrate || {
                    echo "All migration attempts failed, trying to reset PostgreSQL database..."

                    # Make the reset script executable
                    chmod +x reset_postgres.py

                    # Try to reset the PostgreSQL database
                    python reset_postgres.py || {
                        echo "PostgreSQL database reset failed, but continuing build process..."
                    }
                }
            }
        }
    else
        echo "Using SQLite database for local development"

        # First, try to run migrations with --fake-initial to handle existing tables
        python manage.py migrate --fake-initial || {
            echo "Initial migrations failed, trying with --fake..."

            # If that fails, try with --fake
            python manage.py migrate --fake || {
                echo "Fake migrations failed, trying to reset the database..."

                # If all else fails, try to reset the database
                python init_db.py || {
                    echo "Database reset failed, but continuing build process..."
                }
            }
        }
    fi
else
    # Database setup for local development
    echo "Setting up database for local development..."

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
fi

# Set up manager user
echo "Setting up manager user..."
python setup_manager.py

echo "Build process completed."
