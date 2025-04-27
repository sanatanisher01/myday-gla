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
        # We don't need to store the tables, just drop the schema
        cursor.fetchall()

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

def ensure_tables_exist():
    """Ensure that all required tables exist in the database."""
    try:
        # Set Django settings module
        os.environ['DJANGO_SETTINGS_MODULE'] = 'myday.settings_prod'

        # Run migrations without --fake to create tables
        print("Running migrations to create tables...")
        result = os.system("python manage.py migrate --noinput")

        if result != 0:
            print("Migration failed, trying to create session table manually...")
            # Connect to the database
            from django.db import connection
            cursor = connection.cursor()

            # Check if django_session table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'django_session'
                );
            """)
            session_table_exists = cursor.fetchone()[0]

            if not session_table_exists:
                print("Creating django_session table manually...")
                cursor.execute("""
                    CREATE TABLE django_session (
                        session_key varchar(40) NOT NULL PRIMARY KEY,
                        session_data text NOT NULL,
                        expire_date timestamp with time zone NOT NULL
                    );
                    CREATE INDEX django_session_expire_date_idx ON django_session (expire_date);
                """)
                print("django_session table created successfully.")

            # Check for other critical tables
            tables_to_check = [
                'auth_user',
                'accounts_userprofile',
                'events_event',
                'bookings_booking'
            ]

            for table in tables_to_check:
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = '{table}'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                if not table_exists:
                    print(f"Table {table} does not exist. Running migrations again...")
                    os.system("python manage.py migrate --noinput")
                    break

        return True
    except Exception as e:
        print(f"Error ensuring tables exist: {e}")
        return False

if __name__ == '__main__':
    success = reset_postgres_database()
    if success:
        print("Now run migrations to recreate the tables.")
        # Ensure all tables exist
        ensure_tables_exist()
        # Create superuser
        os.system("python setup_manager.py")
    else:
        print("Database reset failed.")
        sys.exit(1)
