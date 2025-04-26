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
                # Create the superuser with a last_login value to avoid null constraint
                from django.utils import timezone
                user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
                user.last_login = timezone.now()
                user.save()
                self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
            else:
                self.stdout.write('Superuser already exists')
        except Exception as e:
            self.stdout.write(f"Error creating superuser: {e}")

            # Try a direct SQL approach if the ORM approach fails
            try:
                with connection.cursor() as cursor:
                    # Check if the user already exists
                    cursor.execute("SELECT COUNT(*) FROM auth_user WHERE username = 'admin'")
                    count = cursor.fetchone()[0]

                    if count == 0:
                        # Insert the superuser directly with SQL
                        from django.utils import timezone
                        from django.contrib.auth.hashers import make_password

                        now = timezone.now()
                        password = make_password('admin123')

                        cursor.execute("""
                            INSERT INTO auth_user
                            (username, email, password, is_superuser, is_staff, is_active, date_joined, last_login, first_name, last_name)
                            VALUES
                            ('admin', 'admin@example.com', %s, TRUE, TRUE, TRUE, %s, %s, '', '')
                        """, [password, now, now])

                        self.stdout.write(self.style.SUCCESS('Superuser created with SQL successfully'))
            except Exception as e2:
                self.stdout.write(f"Error creating superuser with SQL: {e2}")

        # Create a sample event and categories
        try:
            # First, check if we have any admin user
            admin_user = None
            try:
                admin_user = User.objects.get(username='admin')
            except User.DoesNotExist:
                # Try to get any superuser
                admin_user = User.objects.filter(is_superuser=True).first()

                if not admin_user:
                    # If no superuser exists, create one
                    from django.utils import timezone
                    admin_user = User.objects.create_superuser(
                        username='admin',
                        email='admin@example.com',
                        password='admin123'
                    )
                    admin_user.last_login = timezone.now()
                    admin_user.save()
                    self.stdout.write(self.style.SUCCESS('Created admin user for sample event'))

            # Now create a main event if none exists
            if not Event.objects.exists():
                event = Event.objects.create(
                    name='Sample Event',
                    description='This is a sample event created during initialization',
                    created_by=admin_user
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

            # Try a direct SQL approach if the ORM approach fails
            try:
                with connection.cursor() as cursor:
                    # Check if we have any events
                    cursor.execute("SELECT COUNT(*) FROM events_event")
                    event_count = cursor.fetchone()[0]

                    if event_count == 0:
                        # Get or create an admin user
                        cursor.execute("SELECT id FROM auth_user WHERE is_superuser = TRUE LIMIT 1")
                        admin_id_result = cursor.fetchone()

                        if admin_id_result:
                            admin_id = admin_id_result[0]
                        else:
                            # No admin user found, we can't proceed
                            self.stdout.write("No admin user found, can't create sample event with SQL")
                            return

                        # Create a sample event
                        from django.utils import timezone
                        now = timezone.now()

                        cursor.execute("""
                            INSERT INTO events_event
                            (name, description, created_at, updated_at, created_by_id, slug)
                            VALUES
                            ('Sample Event', 'This is a sample event created during initialization', %s, %s, %s, 'sample-event')
                            RETURNING id
                        """, [now, now, admin_id])

                        event_id = cursor.fetchone()[0]

                        # Create a sub-event
                        cursor.execute("""
                            INSERT INTO events_subevent
                            (name, description, price, created_at, updated_at, event_id)
                            VALUES
                            ('Sample Sub-Event', 'This is a sample sub-event', 1000, %s, %s, %s)
                            RETURNING id
                        """, [now, now, event_id])

                        sub_event_id = cursor.fetchone()[0]

                        # Create categories
                        categories = ['Wedding', 'Birthday', 'Corporate', 'Festival', 'Other']
                        for category_name in categories:
                            cursor.execute("""
                                INSERT INTO events_category
                                (name, description, price, created_at, updated_at, sub_event_id)
                                VALUES
                                (%s, %s, 500, %s, %s, %s)
                            """, [category_name, f'Sample {category_name} category', now, now, sub_event_id])

                        self.stdout.write(self.style.SUCCESS('Sample event, sub-event, and categories created with SQL successfully'))
            except Exception as e2:
                self.stdout.write(f"Error creating sample event with SQL: {e2}")

        # Additional initialization can be added here if needed
