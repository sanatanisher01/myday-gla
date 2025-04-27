from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0009_chatmessage_file_url_chatmessage_message_type_and_more'),
    ]

    operations = [
        # Add only the message_type field
        migrations.AddField(
            model_name='chatmessage',
            name='message_type',
            field=models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video'), ('file', 'File')], default='text', max_length=10),
        ),
    ]
