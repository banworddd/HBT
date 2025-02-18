import random
import string

def code_generation(username):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    print(f'Спасибо за регистрацию,{username}, ваш код для подтверждения учетной записи {code}')
    return code