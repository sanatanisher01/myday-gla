from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0010_ensure_fields_exist'),
        ('chat', '0011_add_message_type_field'),
        ('chat', '0011_merge_20240527_migration'),
    ]

    operations = [
        # No operations needed, just merging migrations
    ]
