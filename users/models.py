from django.db import models
from django.contrib.auth.models import AbstractUser
from uuid import uuid4
import os

def generate_avatar_name(instance, filename):
    extension = filename.split('.')[-1]
    new_filename = uuid4().hex + '.' +extension
    return os.path.join('avatars/', new_filename)

class CustomUser(AbstractUser):
    username = models.CharField(max_length=50, unique=True )
    public_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=120, blank=True, null=True, default='')
    is_confirmed = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=generate_avatar_name, blank=True, null=True, default='avatars/default.png')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        related_query_name='custom_user',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        related_query_name='custom_user',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Chats(models.Model):
    user_1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chats_as_user_1')
    user_2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chats_as_user_2')


class Message(models.Model):
    text = models.TextField()
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recipient')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sender')
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE)
    send_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.text





