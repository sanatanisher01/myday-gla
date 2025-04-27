#!/usr/bin/env python
"""
Script to reset the PostgreSQL database on Render.
This script will drop all tables and recreate them.
"""
import os
import sys
import django
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myday.settings_prod')
django.setup()

from django.conf import settings

def reset_postgres_database():
    """Reset the PostgreSQL database by dropping and recreating all tables."""
    if 'DATABASE_URL' not in os.environ:
        print("No DATABASE_URL found. Exiting.")
        return False

    try:
        # Get database connection parameters from settings
        db_settings = settings.DATABASES['default']
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_password = db_settings['PASSWORD']
        db_host = db_settings['HOST']
        db_port = db_settings['PORT']

        print(f"Connecting to PostgreSQL database: {db_name} on {db_host}")

        # Connect to the database
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Get all tables in the public schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """)
        tables = cursor.fetchall()

        # Drop all tables
        print("Dropping all tables...")
        cursor.execute("DROP SCHEMA public CASCADE;")
        cursor.execute("CREATE SCHEMA public;")
        cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
        cursor.execute("GRANT ALL ON SCHEMA public TO public;")

        print("Database reset successful.")
        conn.close()
        return True

    except Exception as e:
        print(f"Error resetting database: {e}")
        return False

if __name__ == '__main__':
    success = reset_postgres_database()
    if success:
        print("Now run migrations to recreate the tables.")
        # Run migrations
        os.system("python manage.py migrate")
        # Create superuser
        os.system("python setup_manager.py")
    else:
        print("Database reset failed.")
        sys.exit(1)
