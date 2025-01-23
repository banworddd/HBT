import random
import string

from django.shortcuts import redirect
from .models import CustomUser


def code_generation(email, username):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    print(f'Спасибо за регистрацию,{username}, ваш код для подтверждения учетной записи {code}')
    return code

def check_user_status(request):
    if not request.user.is_authenticated:
        return redirect('startpage')

    try:
        user = CustomUser.objects.get(email=request.user.email)
    except CustomUser.DoesNotExist:
        return redirect('startpage')

    if not user.is_confirmed:
        return redirect('emailconfirmation')

    return None


