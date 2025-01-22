from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Groups, GroupSubscribers

@receiver(post_save, sender=Groups)
def create_group_subscriber(sender, instance, created, **kwargs):
    if created:
        GroupSubscribers.objects.create(group=instance, user=instance.creator, is_admin=True)