from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration is a no-op since the ChatRoom model has already been removed.
    """

    dependencies = [
        ('chat', '0005_fix_chatmessage_model'),
    ]

    operations = [
        # No operations needed
    ]
