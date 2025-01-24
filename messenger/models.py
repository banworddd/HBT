from django.db import models
from users.models import CustomUser
from django.core.exceptions import ValidationError

class Chats(models.Model):
    user_1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chats_as_user_1')
    user_2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chats_as_user_2')

    class Meta:
        unique_together = (('user_1', 'user_2'),)

    def save(self, *args, **kwargs):
        if Chats.objects.filter(user_1=self.user_2, user_2=self.user_1).exists():
            raise ValidationError('Chat with these users already exists.')
        super().save(*args, **kwargs)


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





