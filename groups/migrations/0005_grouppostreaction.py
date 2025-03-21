# Generated by Django 5.1.5 on 2025-02-05 15:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0004_grouppostscomments'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupPostReaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(blank=True, choices=[('L', 'Like'), ('D', 'Dislike'), ('H', 'Heart')], max_length=1)),
                ('reaction_time', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.groupposts')),
                ('react_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.groupsubscribers')),
            ],
            options={
                'unique_together': {('post', 'react_user')},
            },
        ),
    ]
