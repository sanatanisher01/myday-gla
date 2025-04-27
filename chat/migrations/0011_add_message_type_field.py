from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0010_ensure_fields_exist'),
    ]

    operations = [
        # Add the message_type field if it doesn't exist
        migrations.AddField(
            model_name='chatmessage',
            name='message_type',
            field=models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video'), ('file', 'File')], default='text', max_length=10),
        ),
        # Add the file_url field if it doesn't exist
        migrations.AddField(
            model_name='chatmessage',
            name='file_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
