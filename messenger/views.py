from users.models import CustomUser
from django.shortcuts import render, redirect, get_object_or_404


def startpage(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(email=request.user.email)
        if user.is_confirmed is False:
            return redirect ('emailconfirmation')
        return redirect('chats', username=user.username)
    count = CustomUser.objects.count()
    return render(request, 'messenger/startpage.html', context={'count':count})





