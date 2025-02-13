from django.utils import timezone

from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache

from common.utils import check_user_status, check_user_session, check_active_sessions
from users.models import CustomUser

from .forms import MessageForm, GroupChatForm
from .models import Chats, Message

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

def group_messages(request, chat_id):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    chat = get_object_or_404(Chats, id = chat_id)
    messages = Message.objects.filter(chat=chat)
    chat_data = {'chat': chat, 'messages': messages}
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            author = request.user
            text = form.cleaned_data['text']
            picture = form.cleaned_data['picture']
            new_message = Message.objects.create(text=text, author=author, chat=chat, picture=picture)
            new_message.save()
            chat.last_message_time = timezone.now()
            chat.save()
            return redirect('group_messages', chat_id=chat.id)
        else:
            chat_data = {'chat': chat, 'messages': messages}
            return render (request, 'messenger/group_messages.html', chat_data)
    else:
        form = MessageForm()
    chat_data = {'chat': chat, 'messages': messages}
    print(messages)
    return render(request, 'messenger/group_messages.html', {'chat_data':chat_data, 'form': form})


def deletemessage(request, message_id):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    message = get_object_or_404(Message, pk=message_id)
    chat = message.chat
    other_user = chat.user_1 if chat.user_2 == request.user else chat.user_2
    if message.is_deleted:
        return redirect('messages', chat_id=message.chat.id)
    message.is_deleted = True
    message.text = 'Сообщение удалено'
    message.picture = None
    message.save()
    return redirect('messages', chat_id=message.chat.id)


def deletecontact(request, contact_name):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    user = get_object_or_404(CustomUser, pk=request.user.id)
    for value in user.contacts:
        if value == contact_name:
            user.contacts[contact_name].delete()
    user.save()
    return redirect('profile', username=contact_name)

def profileview(request, username):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response
    request_user = get_object_or_404(CustomUser, pk=request.user.id)
    is_contact = False
    for contact in request_user.contacts:
        if contact == username:
            is_contact = True

    cached_user_data = cache.get(f"messenger_profile_{username}")
    if cached_user_data:
        return render(request, 'messenger/profile.html', cached_user_data)
    user = get_object_or_404(CustomUser, username=username)
    user_online = check_user_session(request, user.id)
    if Chats.objects.filter(Q(user_1=request.user.id) & Q(user_2=request.user.id) & Q(user_2=request.user.id) & Q(user_1=request.user.id)).exists():
        chat = Chats.objects.get(Q(user_1=request.user.id) & Q(user_2=request.user.id) & Q(user_2=request.user.id) & Q(user_1=request.user.id))
        chat_id = chat.id
    else:
        chat_id = None
    user_data = {
        'user_online': user_online,
        'avatar': user.avatar,
        'public_name': user.public_name,
        'username': user.username,
        'status': user.status,
        'reg_date': user.date_joined,
        'chat_id': chat_id,
        'is_contact': is_contact,
    }
    cache.set(f"messenger_profile_{username}", user_data, timeout=300)
    return render(request, 'messenger/profile.html', user_data)


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










