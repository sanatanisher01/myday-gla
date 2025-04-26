from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration completely resets the Category table.
    It drops the existing table and recreates it with the correct schema.
    """

    dependencies = [
        ('events', '0005_fix_category_model'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL to run - completely reset the Category table
            """
            -- First, drop any existing Category table
            DROP TABLE IF EXISTS events_category CASCADE;
            
            -- Then create the table with the correct schema
            CREATE TABLE events_category (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT NULL,
                price NUMERIC(10, 2) NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                sub_event_id INTEGER NOT NULL REFERENCES events_subevent(id)
            );
            
            -- Update the django_migrations table to mark this migration as applied
            UPDATE django_migrations 
            SET applied = TRUE 
            WHERE app = 'events' AND name = '0006_reset_category_table';
            """,
            # SQL to run when reversing the migration (empty because we can't easily restore the old state)
            ""
        ),
    ]
