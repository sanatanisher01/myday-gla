import os
import shutil
import sqlite3
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent

# Path to the SQLite database
DB_PATH = BASE_DIR / 'db.sqlite3'

# Connect to the SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Delete all migration records for the chat app from django_migrations
print("Deleting migration records for chat app...")
cursor.execute("DELETE FROM django_migrations WHERE app = 'chat'")
conn.commit()

# Drop the chat_chatmessage table if it exists
print("Dropping chat_chatmessage table...")
cursor.execute("DROP TABLE IF EXISTS chat_chatmessage")
conn.commit()

# Close the database connection
conn.close()

# Delete all migration files in the chat/migrations directory except __init__.py
migrations_dir = BASE_DIR / 'chat' / 'migrations'
print(f"Deleting migration files in {migrations_dir}...")
for file_path in migrations_dir.glob('*.py'):
    if file_path.name != '__init__.py':
        print(f"Deleting {file_path}")
        os.remove(file_path)

# Create a new initial migration file
print("Creating new initial migration file...")
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

print("Migration reset complete!")
