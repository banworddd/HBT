import random
import string
import uuid
import os

def code_generation(email, username):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    print(f'Спасибо за регистрацию,{username}, ваш код для подтверждения учетной записи {code}')
    return code

def generate_avatar_name(instance, filename):
    extension = filename.split('.')[-1]
    new_filename = uuid.uuid4().hex + '.' +extension
    return os.path.join('avatars/', new_filename)



