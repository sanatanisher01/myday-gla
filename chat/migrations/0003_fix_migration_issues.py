from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration is a fix for the issue where the previous migration
    tries to remove columns that don't exist in the database.
    """

    dependencies = [
        ('chat', '0002_remove_chatmessage_image_remove_chatmessage_room_and_more'),
    ]

    operations = [
        # No operations needed, this is just to ensure the migration history is consistent
    ]
