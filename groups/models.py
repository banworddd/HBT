from django.db import models
from users.models import  CustomUser
from django.utils.crypto import get_random_string
from slugify import slugify
from datetime import datetime

from .utils import generate_image_name, generate_avatar_name
from .managers import ActiveGroupManager

class Groups(models.Model):
    name = models.CharField(max_length=50, unique=True)
    public_name = models.CharField(max_length=100)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='creator')
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=generate_avatar_name, default='groups_avatars/default.png')
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_groups = ActiveGroupManager()

    def save(self, *args, **kwargs):
        self.name = '@' + self.name.lower()
        super(Groups, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class GroupSubscribers(models.Model):
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    subscription_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('group', 'user'),)

class GroupPosts(models.Model):
    group = models.ForeignKey(Groups,on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    post = models.TextField()
    author = models.ForeignKey('GroupSubscribers', on_delete=models.SET_NULL, limit_choices_to={'is_admin': True}, blank=True, null=True)
    author_name = models.CharField(max_length=100, default='Anonymous')
    pub_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_edit = models.BooleanField(default=False)
    picture1 = models.ImageField(upload_to=generate_image_name, blank=True, null=True)
    picture2 = models.ImageField(upload_to=generate_image_name, blank=True, null=True)
    picture3 = models.ImageField(upload_to=generate_image_name, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            current_date = datetime.now().strftime('%d-%m-%Y')
            random_id = get_random_string(length=4, allowed_chars='0123456789')
            self.slug = f'{base_slug}-{current_date}-{random_id}'
        super(GroupPosts, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class GroupPostsEdits(models.Model):
    post = models.ForeignKey(GroupPosts, on_delete=models.CASCADE)
    edit_date = models.DateTimeField(auto_now=True)
    edit_author = models.ForeignKey('GroupSubscribers', on_delete=models.CASCADE)
    edit_author_name = models.CharField(max_length=100, default='Anonymous')
    post_previous = models.TextField()
    post_next = models.TextField()
    class Meta:
        unique_together = (('post', 'edit_date'),)

class GroupPostsComments(models.Model):
    post = models.ForeignKey(GroupPosts, on_delete=models.CASCADE)
    comment = models.TextField(max_length=240)
    comment_author = models.ForeignKey('GroupSubscribers', on_delete=models.CASCADE)
    comment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment

class GroupPostReaction(models.Model):
    STATUS_CHOICES = [
        ('L', 'Like'),
        ('D', 'Dislike'),
        ('H','Heart')
    ]

    post = models.ForeignKey(GroupPosts, on_delete=models.CASCADE)
    react_user = models.ForeignKey('GroupSubscribers', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True)
    reaction_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('post', 'react_user'),)

    def __str__(self):
        return self.status


