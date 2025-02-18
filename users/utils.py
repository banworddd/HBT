import uuid
import os

def generate_avatar_name(instance, filename):
    extension = filename.split('.')[-1]
    new_filename = uuid.uuid4().hex + '.' +extension
    return os.path.join('users_avatars/', new_filename)



