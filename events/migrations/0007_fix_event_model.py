from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration fixes the Event model by ensuring the cover_photo field is nullable.
    """

    dependencies = [
        ('events', '0006_reset_category_table'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL to run - update the Event table schema
            """
            -- Make cover_photo nullable
            ALTER TABLE events_event ALTER COLUMN cover_photo DROP NOT NULL;
            
            -- Update the django_migrations table to mark this migration as applied
            UPDATE django_migrations 
            SET applied = TRUE 
            WHERE app = 'events' AND name = '0007_fix_event_model';
            """,
            # SQL to run when reversing the migration (empty because we can't easily restore the old state)
            ""
        ),
    ]
