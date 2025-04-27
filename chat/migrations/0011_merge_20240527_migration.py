from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration merges the conflicting migrations:
    - 0004_fix_migration_conflict
    - 0010_ensure_fields_exist
    """

    dependencies = [
        ('chat', '0004_fix_migration_conflict'),
        ('chat', '0010_ensure_fields_exist'),
    ]

    operations = [
        # This is an empty migration that just merges the two branches
    ]
