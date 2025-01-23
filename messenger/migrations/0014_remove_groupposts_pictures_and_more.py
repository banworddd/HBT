# Generated by Django 5.1.5 on 2025-01-23 14:19

import messenger.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0013_alter_grouppostpictures_picture1_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupposts',
            name='pictures',
        ),
        migrations.RemoveField(
            model_name='groupposts',
            name='thumbnail',
        ),
        migrations.AddField(
            model_name='groupposts',
            name='picture1',
            field=models.ImageField(blank=True, null=True, upload_to=messenger.models.generate_image_name),
        ),
        migrations.AddField(
            model_name='groupposts',
            name='picture2',
            field=models.ImageField(blank=True, null=True, upload_to=messenger.models.generate_image_name),
        ),
        migrations.AddField(
            model_name='groupposts',
            name='picture3',
            field=models.ImageField(blank=True, null=True, upload_to=messenger.models.generate_image_name),
        ),
        migrations.DeleteModel(
            name='GroupPostPictures',
        ),
    ]
