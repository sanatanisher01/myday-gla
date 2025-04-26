from django.db import migrations, models

class Migration(migrations.Migration):
    """
    This migration is a fix for the issue where the previous migration
    tries to remove columns that don't exist in the database.

    It creates a fresh schema for the ChatMessage model to ensure consistency.
    """

    dependencies = [
        ('chat', '0002_remove_chatmessage_image_remove_chatmessage_room_and_more'),
    ]

    operations = [
        # First, we'll drop the existing table and recreate it with the correct schema
        migrations.RunSQL(
            # SQL to run - drop and recreate the table
            """
            DROP TABLE IF EXISTS chat_chatmessage;
            CREATE TABLE chat_chatmessage (
                id SERIAL PRIMARY KEY,
                message TEXT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                sender_id INTEGER NOT NULL REFERENCES auth_user(id),
                receiver_id INTEGER NOT NULL REFERENCES auth_user(id)
            );
            """,
            # SQL to run when reversing the migration (empty because we can't easily restore the old state)
            ""
        ),
    ]
