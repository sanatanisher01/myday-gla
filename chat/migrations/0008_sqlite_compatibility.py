from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration ensures compatibility with SQLite by using a different approach.
    """

    dependencies = [
        ('chat', '0007_delete_chatroom'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL to run for SQLite compatibility
            """
            -- This is a no-op migration for SQLite compatibility
            SELECT 1;
            """,
            # SQL to run when reversing the migration
            "SELECT 1;"
        ),
    ]
