from django.shortcuts import redirect
from users.models import CustomUser

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
