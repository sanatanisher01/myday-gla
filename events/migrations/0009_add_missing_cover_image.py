from django.db import migrations, models

class Migration(migrations.Migration):
    """
    This migration adds the missing cover_image field to the SubEvent model.
    """

    dependencies = [
        ('events', '0008_alter_event_cover_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='subevent',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='sub_events/'),
        ),
    ]
