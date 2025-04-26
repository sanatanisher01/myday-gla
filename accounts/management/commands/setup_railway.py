from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Sets up the database for Railway deployment'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Railway setup...'))
        
        # Check if we're using SQLite
        using_sqlite = 'sqlite3' in connection.vendor
        self.stdout.write(f'Using database: {connection.vendor}')
        
        if using_sqlite:
            self.stdout.write(self.style.WARNING('SQLite detected. Applying special handling...'))
            
            # Create tables manually if needed
            with connection.cursor() as cursor:
                # Check if ChatMessage table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_chatmessage';")
                if not cursor.fetchone():
                    self.stdout.write(self.style.WARNING('Creating chat_chatmessage table...'))
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_chatmessage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        FOREIGN KEY (sender_id) REFERENCES auth_user (id),
                        FOREIGN KEY (receiver_id) REFERENCES auth_user (id)
                    );
                    """)
        
        # Create a superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Creating admin superuser...'))
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password=os.environ.get('ADMIN_PASSWORD', 'admin123')
            )
            self.stdout.write(self.style.SUCCESS('Admin superuser created!'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin superuser already exists.'))
        
        self.stdout.write(self.style.SUCCESS('Railway setup completed successfully!'))
