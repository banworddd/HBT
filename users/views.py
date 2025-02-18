from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserEditionForm, CustomUserConfirmationForm, CustomLoginForm
from django.contrib.auth import login, authenticate
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth import logout
from groups.models import GroupSubscribers
from common.utils import check_user_status, check_user_session
from django.core.cache import cache


def registration(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(email=request.user.email)
        return redirect('chats')



    return render(request, 'users/registration.html')


def email_confirmation(request):
    print(request.session['confirmation_code'])
    return render(request, 'users/email_confirmation.html')

def login_page(request):

    if request.user.is_authenticated:
        return redirect('chats')

    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('startpage')


def profileview(request):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    # Пытаемся получить данные из кеша
    cached_user_data = cache.get(f"profile_{request.user.username}")

    if cached_user_data:
        return render(request, 'users/profile.html', cached_user_data)
    user = get_object_or_404(CustomUser, username =request.user.username)
    groups = GroupSubscribers.objects.filter(user=user)
    user_online = check_user_session(request, user.id)
    user_data = {
        'user_online': user_online,
        'avatar': user.avatar,
        'public_name': user.public_name,
        'username': user.username,
        'email': user.email,
        'status': user.status,
        'reg_date': user.date_joined,
        'groups': groups,
    }

    # Кешируем данные на 15 минут
    cache.set(f"profile_{request.user.username}", user_data, timeout=900)

    return render(request, 'users/profile.html', user_data)
def edit_profile(request):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    user = get_object_or_404(CustomUser, username=request.user.username)

    if request.method == 'POST':
        form = CustomUserEditionForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            username = '@' + form.cleaned_data.get('username').lower()

            user_online = check_user_session(request, user.id)
            user_data = {
                'user_online': user_online,
                'avatar': user.avatar,
                'public_name': user.public_name,
                'username': user.username,
                'status': user.status,
                'request_user': request.user,
            }

            # Кешируем данные на 15 минут
            return redirect('profile')

    else:
        form = CustomUserEditionForm(instance=user)

    return render (request, 'users/edit_profile.html', {'form': form})





