from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration removes the ChatRoom model.
    """

    dependencies = [
        ('chat', '0005_fix_chatmessage_model'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL to run - drop the ChatRoom table
            """
            -- Drop the ChatRoom table if it exists
            DROP TABLE IF EXISTS chat_chatroom CASCADE;
            DROP TABLE IF EXISTS chat_chatroom_users CASCADE;
            
            -- Update the django_migrations table to mark this migration as applied
            UPDATE django_migrations 
            SET applied = TRUE 
            WHERE app = 'chat' AND name = '0006_remove_chatroom_model';
            """,
            # SQL to run when reversing the migration (empty because we can't easily restore the old state)
            ""
        ),
    ]
