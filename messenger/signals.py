from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Message, Chats, MessageReaction
from users.models import CustomUser
from django.core.cache import cache

@receiver(post_save, sender=Message)
def message_post_save_handler(sender, instance, created, **kwargs):
    chat = Chats.objects.filter(id=instance.chat.id).first()
    other_user = chat.user_1 if chat.user_2 == instance.author else chat.user_2
    cache.delete(f"messages_{instance.chat.id}_{instance.author.id}")
    cache.delete(f"messages_{instance.chat.id}_{other_user.id}")

@receiver(post_delete, sender=Message)
def message_post_save_handler(sender, instance, deleted, **kwargs):
    chat = Chats.objects.filter(id=instance.chat.id).first()
    other_user = chat.user_1 if chat.user_2 == instance.author else chat.user_2
    cache.delete(f"messages_{instance.chat.id}_{instance.author.id}")
    cache.delete(f"messages_{instance.chat.id}_{other_user.id}")

@receiver(post_save, sender=CustomUser)
def user_profile_save_handler(sender, instance, created, **kwargs):
    cache.delete(f"profile_{instance.username}")
    cache.delete(f"messenger_profile_{instance.username}")

@receiver(post_save, sender=MessageReaction)
def message_reaction_post_save_handler(sender, instance, created, **kwargs):
    user = CustomUser.objects.get(username=instance.react_user)
    chat = Chats.objects.filter(id=instance.message.chat_id).first()
    other_user = chat.user_1 if chat.user_2 == user else chat.user_2
    cache.delete(f"messages_{chat.id}_{user.id}")
    cache.delete(f"messages_{chat.id}_{other_user.id}")

