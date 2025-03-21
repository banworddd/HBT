# Generated by Django 5.1.5 on 2025-02-06 10:07

import django.db.models.deletion
import messenger.utils
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats_as_user_1', to=settings.AUTH_USER_MODEL)),
                ('user_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats_as_user_2', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user_1', 'user_2')},
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('send_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('S', 'Sender'), ('R', 'Read')], default='S', max_length=1)),
                ('picture', models.ImageField(blank=True, null=True, upload_to=messenger.utils.generate_image_name)),
                ('is_deleted', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='messenger.chats')),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
            },
        ),
        migrations.CreateModel(
            name='MessageReaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(blank=True, choices=[('L', 'Like'), ('D', 'Dislike'), ('H', 'Heart')], max_length=1)),
                ('reaction_time', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='messenger.message')),
                ('react_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='react_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('message', 'react_user')},
            },
        ),
    ]
