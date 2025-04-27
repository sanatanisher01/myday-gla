#!/usr/bin/env python
"""
Script to check the database connection and tables.
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myday.settings_prod')
django.setup()

from django.db import connection

def main():
    print("Checking database connection...")
    
    # Print database configuration
    from django.conf import settings
    print(f"Database engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"Database name: {settings.DATABASES['default']['NAME']}")
    
    # Check if we can connect to the database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"Database connection successful: {result}")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    # Check what tables exist
    try:
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
            print(f"Total tables: {len(tables)}")
            
            # Check for core Django tables
            core_tables = ['django_migrations', 'auth_user', 'django_content_type', 'auth_permission']
            for table in core_tables:
                if table in tables:
                    print(f"✅ {table} exists")
                else:
                    print(f"❌ {table} does not exist")
    except Exception as e:
        print(f"Error checking tables: {e}")

if __name__ == "__main__":
    main()
