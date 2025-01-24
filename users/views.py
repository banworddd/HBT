from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserEditionForm, CustomUserConfirmationForm, CustomLoginForm
from django.contrib.auth import login, authenticate
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth import logout
from groups.models import GroupSubscribers
from common.utils import check_user_status
from .utils import  code_generation


def registration(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(email=request.user.email)
        return redirect('chats', username=user.username)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            print(username)
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
            return redirect('emailconfirmation')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/registration.html', {'form': form})


def email_confirmation(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(email=request.user.email)
        if user.is_confirmed is True:
            return redirect('chats', username=user.username)
        if 'confirmation_code' not in request.session:
            request.session['confirmation_code'] = code_generation(user.email, user.username)
        if request.method == 'POST':
            form = CustomUserConfirmationForm(request.POST)
            if form.is_valid():
                user_code = form.cleaned_data.get('confirmation_code')
                if user_code == request.session['confirmation_code']:
                    user.is_confirmed = True
                    user.save()
                    return redirect('chats', username=user.username)
                else:
                    messages.error(request, 'Неправильный код подтверждения')
        else:
            form = CustomUserConfirmationForm()
        return render(request, 'users/email_confirmation.html', {'form': form})
    else:
        return redirect('reg')

def login_view(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(email=request.user.email)
        if not user.is_confirmed:
            return redirect('emailconfirmation')
        return redirect('chats', username=user.username)

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('chats', username=user.username)
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = CustomLoginForm()

    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('startpage')

def profileview(request, username):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    user = get_object_or_404(CustomUser, username=username)
    groups = GroupSubscribers.objects.filter(user=user)

    if request.method == 'POST' and request.user.username == username:
        form = CustomUserEditionForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', username=form.instance.username)
    else:
        form = CustomUserEditionForm(instance=user)
    user_data = {
        'avatar' : user.avatar,
        'public_name': user.public_name,
        'username': user.username,
        'email': user.email,
        'status': user.status,
        'reg_date': user.date_joined,
        'groups': groups,
        'request_user': request.user,
        'form': form,
    }
    return render(request, 'users/profile.html', user_data)





