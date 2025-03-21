# Generated by Django 5.1.5 on 2025-02-12 11:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0008_message_is_edited'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='dislikes',
        ),
        migrations.RemoveField(
            model_name='message',
            name='hearts',
        ),
        migrations.RemoveField(
            model_name='message',
            name='likes',
        ),
        migrations.CreateModel(
            name='MessageReaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reaction', models.CharField(choices=[('L', 'Like'), ('D', 'Dislike'), ('H', 'Heart'), ('B', 'BrokenHeart')], max_length=1)),
                ('reaction_time', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='messenger.message')),
            ],
        ),
    ]
