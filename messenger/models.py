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
    avatar = models.ImageField(upload_to=generate_avatar_name, blank=True, null=True)

    last_message_time = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if self.user_1 and self.user_2 and not self.is_group:
            if Chats.objects.filter(Q(user_1=self.user_2) & Q(user_2=self.user_1) | Q(user_1=self.user_1) & Q(user_2=self.user_2)).exists() and not self.is_group:
                raise ValidationError('Chat with these users already exists.')
        if self.user_1 and self.user_2 and self.is_group:
            raise ValidationError('Wrong fields')

        super().save(*args, **kwargs)


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
    likes = models.ManyToManyField(CustomUser, related_name='likes', blank=True)
    dislikes = models.ManyToManyField(CustomUser, related_name='dislikes', blank=True)
    hearts = models.ManyToManyField(CustomUser, related_name='hearts', blank=True)


    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.text








