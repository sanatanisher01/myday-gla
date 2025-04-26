from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
from events.models import Category, Event, SubEvent
from accounts.models import UserProfile  # Changed from Profile to UserProfile
import os
import sys

class Command(BaseCommand):
    help = 'Initialize the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database initialization...'))

        # Print debug information
        self.stdout.write(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'not set')}")
        self.stdout.write(f"RENDER env var: {os.environ.get('RENDER', 'not set')}")

        # Check if tables exist - works with both SQLite and PostgreSQL
        try:
            db_engine = connection.settings_dict['ENGINE']
            with connection.cursor() as cursor:
                if 'sqlite3' in db_engine:
                    # SQLite query
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                elif 'postgresql' in db_engine:
                    # PostgreSQL query
                    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
                else:
                    # Generic fallback
                    self.stdout.write(f"Unknown database engine: {db_engine}, skipping table check")
                    return

                tables = cursor.fetchall()
                self.stdout.write(f"Tables in database: {tables}")
        except Exception as e:
            self.stdout.write(f"Error checking tables: {e}")

        # Create superuser if it doesn't exist
        try:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
                self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
            else:
                self.stdout.write('Superuser already exists')
        except Exception as e:
            self.stdout.write(f"Error creating superuser: {e}")

        # Create a sample event and categories
        try:
            # First, create a main event
            if not Event.objects.exists():
                event = Event.objects.create(
                    name='Sample Event',
                    description='This is a sample event created during initialization',
                    created_by=User.objects.get(username='admin')
                )
                self.stdout.write(self.style.SUCCESS('Sample event created successfully'))

                # Create a sub-event for this event
                sub_event = SubEvent.objects.create(
                    event=event,
                    name='Sample Sub-Event',
                    description='This is a sample sub-event',
                    price=1000
                )
                self.stdout.write(self.style.SUCCESS('Sample sub-event created successfully'))

                # Create categories for this sub-event
                categories = ['Wedding', 'Birthday', 'Corporate', 'Festival', 'Other']
                for category_name in categories:
                    Category.objects.create(
                        sub_event=sub_event,
                        name=category_name,
                        description=f'Sample {category_name} category',
                        price=500
                    )
                self.stdout.write(self.style.SUCCESS('Categories created successfully'))
            else:
                self.stdout.write('Events already exist, skipping sample event and category creation')
        except Exception as e:
            self.stdout.write(f"Error creating sample event and categories: {e}")

        # Additional initialization can be added here if needed
