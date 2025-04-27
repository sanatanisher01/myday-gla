from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_add_missing_cover_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='subevent',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='sub_events/'),
        ),
    ]
