# Generated by Django 5.1.5 on 2025-02-07 14:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0003_alter_chats_admins_alter_chats_users'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='chats',
            unique_together=set(),
        ),
    ]
