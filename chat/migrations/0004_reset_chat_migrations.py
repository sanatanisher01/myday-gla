from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration completely resets the chat app's database schema.
    It drops the existing tables and recreates them with the correct schema.
    """

    dependencies = [
        ('chat', '0003_fix_migration_issues'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL to run - completely reset the chat app's tables
            """
            -- First, drop any existing tables
            DROP TABLE IF EXISTS chat_chatmessage CASCADE;
            
            -- Then create the tables with the correct schema
            CREATE TABLE chat_chatmessage (
                id SERIAL PRIMARY KEY,
                message TEXT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                sender_id INTEGER NOT NULL REFERENCES auth_user(id),
                receiver_id INTEGER NOT NULL REFERENCES auth_user(id)
            );
            
            -- Update the django_migrations table to mark all chat migrations as applied
            UPDATE django_migrations 
            SET applied = TRUE 
            WHERE app = 'chat';
            """,
            # SQL to run when reversing the migration (empty because we can't easily restore the old state)
            ""
        ),
    ]
