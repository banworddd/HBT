from django.db import models
from django.db.models import Q

from users.models import CustomUser
from django.core.exceptions import ValidationError

from .utils import generate_image_name, generate_avatar_name


class Chats(models.Model):
    user_1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chats_as_user_1', blank=True, null=True)
    user_2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chats_as_user_2', blank=True, null=True)

    is_group = models.BooleanField(default=False)
    users = models.ManyToManyField(CustomUser, related_name='chats', blank=True)
    admins = models.ManyToManyField(CustomUser, related_name='chats_as_admin', blank=True)
    name = models.CharField(max_length=120,blank=True, null=True)
    avatar = models.ImageField(upload_to=generate_avatar_name, blank=True, null=True, default='chats_avatars/default.png')


    def save(self, *args, **kwargs):
        if self.user_1 and self.user_2 and not self.is_group:
            if Chats.objects.filter(Q(user_1=self.user_2) & Q(user_2=self.user_1) | Q(user_1=self.user_1) & Q(user_2=self.user_2)).exists() and not self.is_group:
                raise ValidationError('Чат между этими двумя пользователями уже существует')

        if self.user_1 and self.user_2 and self.is_group:
            raise ValidationError('Заполнены неверные поля пользователей для группы')

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return self.id


class Message(models.Model):
    STATUS_CHOICES = [
        ('S', 'Sender'),
        ('R', 'Read'),
    ]

    text = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='author')
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE)
    send_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='S')
    picture = models.ImageField(upload_to=generate_image_name, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)


    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.text


class MessageReaction(models.Model):
    STATUS_CHOICES = [
        ('L', 'Like'),
        ('D', 'Dislike'),
        ('H', 'Heart'),
        ('B', 'BrokenHeart'),
    ]

    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=1, choices=STATUS_CHOICES)
    reaction_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('reaction', 'message', 'author'),)

    def __str__(self):
        return self.reaction








