from django.db import models
from django.contrib.auth.models import AbstractUser

from .utils import generate_avatar_name


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






