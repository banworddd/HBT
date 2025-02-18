from django.db import models
from django.contrib.auth.models import AbstractUser

from .utils import generate_avatar_name


class CustomUser(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    public_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=120, blank=True, null=True, default='')
    is_confirmed = models.BooleanField(default=False)
    avatar = models.ImageField(
        upload_to=generate_avatar_name, blank=True, null=True, default='users_avatars/default.png'
    )
    contacts = models.ManyToManyField(
        'self', blank=True, related_name='user_contacts', symmetrical=False
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        """
        Переопределяет метод save для добавления символа '@' в начало username,
        если он ещё не начинается с этого символа.
        """
        if not self.username.startswith('@'):
            self.username = '@' + self.username
        super().save(*args, **kwargs)







