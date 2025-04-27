#!/usr/bin/env python
"""
Script to initialize the database from scratch.
This script will:
1. Create all necessary tables
2. Create a superuser
3. Create sample data
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myday.settings_prod')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from django.core.management import call_command
from django.utils import timezone
from django.contrib.auth.hashers import make_password

def main():
    print("Starting database initialization...")

    # Check if we're on Render
    is_render = os.environ.get('RENDER', 'false').lower() == 'true'
    print(f"Running on Render: {is_render}")

    # Check if tables exist
    with connection.cursor() as cursor:
        if 'sqlite3' in connection.settings_dict['ENGINE']:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        elif 'postgresql' in connection.settings_dict['ENGINE']:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        else:
            print(f"Unknown database engine: {connection.settings_dict['ENGINE']}")
            return

        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables in database: {tables}")

    # Handle database initialization differently on Render
    if is_render:
        print("Running on Render - checking database state...")

        # Check if we have migration issues
        if 'django_migrations' in tables and 'auth_user' not in tables:
            print("Migration table exists but auth_user doesn't. Recreating tables...")

            # Close the connection before attempting to modify the database
            connection.close()

            # For SQLite, we can try to delete the database file
            if 'sqlite3' in connection.settings_dict['ENGINE']:
                db_file = connection.settings_dict['NAME']
                if os.path.exists(db_file):
                    try:
                        os.remove(db_file)
                        print(f"Deleted SQLite database file: {db_file}")
                    except Exception as e:
                        print(f"Error deleting SQLite database file: {e}")

            # For PostgreSQL, we can try to drop all tables
            elif 'postgresql' in connection.settings_dict['ENGINE']:
                try:
                    # Reconnect to the database
                    connection.connect()
                    with connection.cursor() as cursor:
                        cursor.execute("DROP SCHEMA public CASCADE;")
                        cursor.execute("CREATE SCHEMA public;")
                        print("Reset PostgreSQL schema")
                except Exception as e:
                    print(f"Error resetting PostgreSQL schema: {e}")

            # Reconnect to the database
            try:
                connection.connect()
                print("Reconnected to database")
            except Exception as e:
                print(f"Error reconnecting to database: {e}")
        else:
            print("Database appears to be in a valid state, proceeding with migrations")

    # Run migrations
    print("Running migrations...")
    call_command('migrate')

    # Create superuser if it doesn't exist
    try:
        if not User.objects.filter(username='admin').exists():
            print("Creating superuser...")
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("Superuser created successfully")
        else:
            print("Superuser already exists")
    except Exception as e:
        print(f"Error creating superuser: {e}")

    # Create sample data
    try:
        from events.models import Event, SubEvent, Category

        # Create a sample event if none exists
        if not Event.objects.exists():
            print("Creating sample event...")
            admin_user = User.objects.get(username='admin')

            event = Event.objects.create(
                name='Sample Event',
                description='This is a sample event created during initialization',
                created_by=admin_user
            )

            # Create a sub-event
            sub_event = SubEvent.objects.create(
                event=event,
                name='Sample Sub-Event',
                description='This is a sample sub-event',
                price=1000
            )

            # Create categories
            categories = ['Wedding', 'Birthday', 'Corporate', 'Festival', 'Other']
            for category_name in categories:
                Category.objects.create(
                    sub_event=sub_event,
                    name=category_name,
                    description=f'Sample {category_name} category',
                    price=500
                )

            print("Sample data created successfully")
        else:
            print("Events already exist, skipping sample data creation")
    except Exception as e:
        print(f"Error creating sample data: {e}")

    print("Database initialization completed")

if __name__ == "__main__":
    main()
