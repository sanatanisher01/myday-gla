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
    
    # If django_migrations exists but not auth_user, we need to recreate the tables
    if 'django_migrations' in tables and 'auth_user' not in tables:
        print("Migration table exists but auth_user doesn't. Recreating tables...")
        
        # Drop all tables
        with connection.cursor() as cursor:
            if 'sqlite3' in connection.settings_dict['ENGINE']:
                # Get all tables except sqlite_sequence
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Drop each table
                for table in tables:
                    print(f"Dropping table {table}...")
                    cursor.execute(f"DROP TABLE IF EXISTS {table};")
            elif 'postgresql' in connection.settings_dict['ENGINE']:
                cursor.execute("DROP SCHEMA public CASCADE;")
                cursor.execute("CREATE SCHEMA public;")
    
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
