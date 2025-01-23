from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserEditionForm, CustomUserConfirmationForm, CustomLoginForm
from django.contrib.auth import login, authenticate
from .models import CustomUser, Chats, Message
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import logout
from messenger.models import GroupSubscribers
from .utils import code_generation, check_user_status


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

def chatsview(request, username):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    user = get_object_or_404(CustomUser, username=username)
    user_id = user.id
    chats = Chats.objects.filter(
        Q(user_1=user_id) | Q(user_2=user_id)
    ).select_related('user_1', 'user_2')

    messages_dict = {}
    for chat in chats:
        other_user = chat.user_2 if chat.user_1.id == user_id else chat.user_1
        last_message = Message.objects.filter(chat=chat).last()
        messages_dict[other_user] = {
            'chat_id': chat.id,
            'message': last_message.text if last_message else None
        }

    return render(request, 'users/chats.html', {'username': username, 'messages': messages_dict})

def messagesview(request, chat_id):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    chat = get_object_or_404(Chats, id=chat_id)
    messages = Message.objects.filter(chat=chat).order_by('send_time')
    request.user = CustomUser.objects.get(id = 1)
    return render(request, 'users/messages.html', {
        "messages": messages,
        "current_user": request.user
    })
def usersview(request):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    users = CustomUser.objects.all()
    return render(request, 'users/users.html', {"users": users})



