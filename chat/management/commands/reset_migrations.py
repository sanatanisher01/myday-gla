import os
import sqlite3
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Resets migrations for the chat app'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting migration reset for chat app...'))

        # Get the base directory
        BASE_DIR = Path(settings.BASE_DIR)

        # Path to the SQLite database
        DB_PATH = BASE_DIR / 'db.sqlite3'

        if os.path.exists(DB_PATH):
            # Connect to the SQLite database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Delete all migration records for the chat app from django_migrations
            self.stdout.write('Deleting migration records for chat app...')
            cursor.execute("DELETE FROM django_migrations WHERE app = 'chat'")
            conn.commit()

            # Drop the chat_chatmessage table if it exists
            self.stdout.write('Dropping chat_chatmessage table...')
            cursor.execute("DROP TABLE IF EXISTS chat_chatmessage")
            conn.commit()

            # Close the database connection
            conn.close()
        else:
            self.stdout.write(self.style.WARNING(f'Database file not found at {DB_PATH}'))

        # Delete all migration files in the chat/migrations directory except __init__.py
        migrations_dir = BASE_DIR / 'chat' / 'migrations'
        self.stdout.write(f'Deleting migration files in {migrations_dir}...')
        for file_path in migrations_dir.glob('*.py'):
            if file_path.name != '__init__.py':
                self.stdout.write(f'Deleting {file_path}')
                os.remove(file_path)

        # Create a new initial migration file
        self.stdout.write('Creating new initial migration file...')
        with open(migrations_dir / '0001_initial.py', 'w') as f:
            f.write("""from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('sender_id', models.IntegerField()),
                ('receiver_id', models.IntegerField()),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
        migrations.RunSQL(
            # SQL to run for SQLite compatibility
            '''
            CREATE INDEX chat_chatmessage_sender_id_idx ON chat_chatmessage (sender_id);
            CREATE INDEX chat_chatmessage_receiver_id_idx ON chat_chatmessage (receiver_id);
            ''',
            # SQL to run when reversing the migration
            '''
            DROP INDEX IF EXISTS chat_chatmessage_sender_id_idx;
            DROP INDEX IF EXISTS chat_chatmessage_receiver_id_idx;
            '''
        ),
    ]
""")

        self.stdout.write(self.style.SUCCESS('Migration reset complete!'))
