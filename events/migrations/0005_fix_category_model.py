from django.db import migrations, models

class Migration(migrations.Migration):
    """
    This migration fixes the Category model by creating a new version
    that matches the current model definition.
    """

    dependencies = [
        ('events', '0004_remove_review_likes'),
    ]

    operations = [
        # Drop and recreate the Category table with the correct schema
        migrations.RunSQL(
            # SQL to run - drop and recreate the table
            """
            DROP TABLE IF EXISTS events_category;
            CREATE TABLE events_category (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT NULL,
                price NUMERIC(10, 2) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
                sub_event_id INTEGER NOT NULL REFERENCES events_subevent(id)
            );
            """,
            # SQL to run when reversing the migration (empty because we can't easily restore the old state)
            ""
        ),
    ]
