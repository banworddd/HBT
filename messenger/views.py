from django.shortcuts import render, redirect, get_object_or_404

from common.utils import check_user_status, check_active_sessions
from users.models import CustomUser

from .forms import  GroupChatForm
from .models import Chats

def startpage(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(email=request.user.email)
        if user.is_confirmed is False:
            return redirect ('emailconfirmation')
        return redirect('chats')
    users_count = CustomUser.objects.count()
    active_user_count = check_active_sessions(request)

    return render(request, 'messenger/startpage.html', context={'users_count':users_count, 'active_user_count':active_user_count})

def chats_view(request):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    username = request.user.username

    return render(request, 'messenger/chats.html', {'username': username})

def chat_detail_view(request, chat_id):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    return render(request, 'messenger/chat_detail.html', {'chat_id': chat_id})

def contactsview(request):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response
    user_id = request.user.id
    return render(request, 'messenger/contacts.html', {'user_id': user_id})


def profileview(request, username):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    if not username.startswith('@'):
        username = '@' + username

    return render(request, 'messenger/profile.html', {'username': username})


def create_group_chat(request):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response
    user = get_object_or_404(CustomUser, username = request.user.username)
    user_set = CustomUser.objects.filter(username=request.user.username)
    if request.method == "POST":
        form = GroupChatForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            users = form.cleaned_data['users']
            all_users = users.union(user_set)
            new_chat = Chats.objects.create(name = name, is_group = True)
            new_chat.users.set(all_users)
            new_chat.admins.add(request.user)
            new_chat.save()
            return redirect('group_messages', chat_id = new_chat.id)
        else:
            return render (request, 'messenger/group_chat.html', {'form': form})
    else:
        form = GroupChatForm()

    return render (request, 'messenger/group_chat.html', {'form': form})










