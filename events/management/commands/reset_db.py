from django.core.management.base import BaseCommand
from django.db import connection
import sys

class Command(BaseCommand):
    help = 'Reset the database schema completely'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset without confirmation',
        )

    def handle(self, *args, **options):
        if not options['force']:
            self.stdout.write(self.style.WARNING('This will completely reset your database. All data will be lost.'))
            self.stdout.write(self.style.WARNING('To proceed, run the command with --force'))
            return

        self.stdout.write(self.style.WARNING('Resetting database schema...'))
        
        try:
            with connection.cursor() as cursor:
                # Get a list of all tables
                if 'postgresql' in connection.settings_dict['ENGINE']:
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        AND table_type = 'BASE TABLE'
                    """)
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    # Drop all tables
                    if tables:
                        # Disable foreign key checks
                        cursor.execute("SET CONSTRAINTS ALL DEFERRED;")
                        
                        for table in tables:
                            self.stdout.write(f"Dropping table {table}...")
                            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                        
                        # Re-enable foreign key checks
                        cursor.execute("SET CONSTRAINTS ALL IMMEDIATE;")
                    
                    self.stdout.write(self.style.SUCCESS('All tables dropped successfully'))
                    
                    # Reset the migrations table
                    cursor.execute("""
                        DROP TABLE IF EXISTS django_migrations;
                        CREATE TABLE django_migrations (
                            id SERIAL PRIMARY KEY,
                            app VARCHAR(255) NOT NULL,
                            name VARCHAR(255) NOT NULL,
                            applied TIMESTAMP WITH TIME ZONE NOT NULL
                        );
                    """)
                    
                    self.stdout.write(self.style.SUCCESS('Migrations table reset'))
                    
                elif 'sqlite3' in connection.settings_dict['ENGINE']:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
                    
                    # Drop all tables
                    for table in tables:
                        self.stdout.write(f"Dropping table {table}...")
                        cursor.execute(f"DROP TABLE IF EXISTS {table};")
                    
                    self.stdout.write(self.style.SUCCESS('All tables dropped successfully'))
                else:
                    self.stdout.write(self.style.ERROR(f"Unsupported database engine: {connection.settings_dict['ENGINE']}"))
                    return
                
            self.stdout.write(self.style.SUCCESS('Database reset complete'))
            self.stdout.write(self.style.SUCCESS('Now run: python manage.py migrate'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error resetting database: {e}"))
            return
