#!/usr/bin/env python
"""
Script to check and fix the django_session table in PostgreSQL.
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myday.settings_prod')
django.setup()

from django.db import connection

def check_and_fix_session_table():
    """Check if django_session table exists and create it if it doesn't."""
    try:
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
            print("django_session table does not exist. Creating it...")
            cursor.execute("""
                CREATE TABLE django_session (
                    session_key varchar(40) NOT NULL PRIMARY KEY,
                    session_data text NOT NULL,
                    expire_date timestamp with time zone NOT NULL
                );
                CREATE INDEX django_session_expire_date_idx ON django_session (expire_date);
            """)
            print("django_session table created successfully.")
            return True
        else:
            print("django_session table already exists.")
            return True
            
    except Exception as e:
        print(f"Error checking/fixing session table: {e}")
        return False

if __name__ == '__main__':
    success = check_and_fix_session_table()
    if not success:
        sys.exit(1)
