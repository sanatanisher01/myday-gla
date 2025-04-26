from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration is a no-op since the previous migration already fixed the ChatMessage model.
    """

    dependencies = [
        ('chat', '0004_reset_chat_migrations'),
    ]

    operations = [
        # No operations needed
    ]
