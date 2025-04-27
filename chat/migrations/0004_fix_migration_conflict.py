from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration is a no-op migration that helps resolve conflicts
    with the chat_chatmessage table already existing.
    """

    dependencies = [
        ('chat', '0003_fix_migration_issues'),
    ]

    operations = [
        # This is an empty migration to help resolve conflicts
    ]
