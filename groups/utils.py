import os
from uuid import uuid4

def generate_image_name(instance, filename):
    extension = filename.split('.')[-1]
    new_filename = uuid4().hex + '.' +extension
    return os.path.join('post_pictures/', new_filename)

def generate_avatar_name(instance, filename):
    extension = filename.split('.')[-1]
    new_filename = uuid4().hex + '.' +extension
    return os.path.join('groups_avatars/', new_filename)
