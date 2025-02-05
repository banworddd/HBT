from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache

from common.utils import check_user_status, check_user_session, check_active_sessions
from users.models import CustomUser
from .forms import MessageForm
from .models import Chats, Message

def startpage(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(email=request.user.email)
        if user.is_confirmed is False:
            return redirect ('emailconfirmation')
        return redirect('chats', username=user.username)
    users_count = CustomUser.objects.count()
    active_user_count = check_active_sessions(request)

    return render(request, 'messenger/startpage.html', context={'users_count':users_count, 'active_user_count':active_user_count})

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

    return render(request, 'messenger/chats.html', {'username': username, 'messages': messages_dict})


def messagesview(request, chat_id):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    chat = get_object_or_404(Chats, id=chat_id)

    messages = Message.objects.filter(chat=chat).select_related('author', 'chat').order_by('send_time')
    other_user = chat.user_1 if chat.user_2 == request.user else chat.user_2
    other_user_status = check_user_session(request, other_user.id)

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            author = request.user
            text = form.cleaned_data['text']
            picture = form.cleaned_data['picture']
            new_message = Message.objects.create(text=text, author=author, chat=chat, picture=picture)
            new_message.save()
            cache.delete(f"messages_{chat_id}_{request.user.id}")
            cache.delete(f"messages_{chat_id}_{other_user.id}")
            return redirect('messages', chat_id=chat.id)
        else:
            chat_data = {
                "messages": [
                    {
                        "id": msg.id,
                        "text": msg.text,
                        "send_time": msg.send_time,
                        "status": msg.status,
                        "is_deleted": msg.is_deleted,
                        "author__username": msg.author.username,
                        "picture_url": msg.picture.url if msg.picture else None,
                    }
                    for msg in messages
                ],
                "other_user": other_user.username,
                "other_user_status": other_user_status,
                "current_user": request.user.username,
                "chat_id": chat_id,
            }
            return render(request, 'messenger/messages.html', {
                "chat_data": chat_data,
                "form": form
            })
    else:
        form = MessageForm()

    cached_chat_data = cache.get(f"messages_{chat_id}_{request.user.id}")
    if cached_chat_data:
        return render(request, 'messenger/messages.html', {'chat_data': cached_chat_data, 'form': form})

    # Обновление статусов непрочитанных сообщений
    unread_messages = messages.filter(author=other_user, status='S')
    unread_messages.update(status='R')

    chat_data = {
        "messages": [
            {
                "id": msg.id,
                "text": msg.text,
                "send_time": msg.send_time,
                "status": msg.status,
                "is_deleted": msg.is_deleted,
                "author__username": msg.author.username,
                "picture_url": msg.picture.url if msg.picture else None,
            }
            for msg in messages
        ],
        "other_user": other_user.username,
        "other_user_status": other_user_status,
        "current_user": request.user.username,
        "chat_id": chat_id,
    }
    cache.set(f"messages_{chat_id}_{request.user.id}", chat_data, timeout=600)
    return render(request, 'messenger/messages.html', {'chat_data': chat_data, 'form': form})


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


def usersview(request):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response


    users = CustomUser.objects.exclude(username=request.user.username)
    chats = Chats.objects.filter(Q(user_1=request.user.id) | Q(user_2=request.user.id))
    chats_with_users = {item: [None, False] for item in users}
    for chat in chats:
        for user in chats_with_users:
            if chat.user_1 == user or chat.user_2==user:
                chats_with_users[user][0]= chat
    for user in chats_with_users.keys():
        chats_with_users[user][1] = check_user_session(request, user.id)

    return render(request, 'messenger/users.html', {"chats_with_users": chats_with_users})

def profileview(request, username):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

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
    }
    cache.set(f"messenger_profile_{username}", user_data, timeout=300)
    return render(request, 'messenger/profile.html', user_data)

def create_chat_view(request, username):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    other_user = get_object_or_404(CustomUser, username=username)
    if Chats.objects.filter(Q(user_1=request.user.id) & Q(user_2 = other_user.id ) |Q(user_2=request.user.id) & Q(user_1 = other_user.id )).exists():
        chat = Chats.objects.filter(Q(user_1=request.user.id) & Q(user_2 = other_user.id ) |Q(user_2=request.user.id) & Q(user_1 = other_user.id ))
        return redirect ('messages', chat_id = chat.id)
    new_chat = Chats.objects.create(user_1=request.user, user_2=other_user)
    new_chat.save()
    return redirect('messages', chat_id = new_chat.id)





