from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration ensures the ChatMessage model has the correct schema.
    """

    dependencies = [
        ('chat', '0004_reset_chat_migrations'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL to run - ensure the ChatMessage table has the correct schema
            """
            -- Drop the table if it exists
            DROP TABLE IF EXISTS chat_chatmessage CASCADE;
            
            -- Create the table with the correct schema
            CREATE TABLE chat_chatmessage (
                id SERIAL PRIMARY KEY,
                message TEXT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                sender_id INTEGER NOT NULL REFERENCES auth_user(id),
                receiver_id INTEGER NOT NULL REFERENCES auth_user(id)
            );
            
            -- Update the django_migrations table to mark this migration as applied
            UPDATE django_migrations 
            SET applied = TRUE 
            WHERE app = 'chat' AND name = '0005_fix_chatmessage_model';
            """,
            # SQL to run when reversing the migration (empty because we can't easily restore the old state)
            ""
        ),
    ]
