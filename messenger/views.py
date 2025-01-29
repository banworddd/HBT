from django.db.models import Q, F
from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache

from common.utils import check_user_status
from users.models import CustomUser
from .forms import MessageForm
from .models import Chats, Message
def startpage(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(email=request.user.email)
        if user.is_confirmed is False:
            return redirect ('emailconfirmation')
        return redirect('chats', username=user.username)
    count = CustomUser.objects.count()
    return render(request, 'messenger/startpage.html', context={'count':count})

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

from django.db.models import F
from django.core.files.storage import default_storage

def messagesview(request, chat_id):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    chat = get_object_or_404(Chats, id=chat_id)

    messages = Message.objects.filter(chat=chat).select_related('author', 'chat').order_by('send_time')
    other_user = chat.user_1 if chat.user_2 == request.user else chat.user_2

    if request.method == 'POST':
        print('post')
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            author = request.user
            text = form.cleaned_data['text']
            picture = form.cleaned_data['picture']
            new_message = Message.objects.create(text=text, author=author, chat=chat, picture=picture)
            new_message.save()
            cache.delete(f"messages_{chat_id}")
            return redirect('messages', chat_id=chat.id)
        else:
            chat_data = {
                "messages": list(messages.values('id', 'text', 'send_time', 'status', 'is_deleted', 'author__username', picture_url=F('picture'))),
                "other_user": other_user.username,
                "current_user": request.user.username,
            }
            return render(request, 'messenger/messages.html', {
                "chat_data": chat_data,
                "form": form
            })
    else:
        form = MessageForm()

    cached_chat_data = cache.get(f"messages_{chat_id}")
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
        "current_user": request.user.username,
    }
    cache.set(f"messages_{chat_id}", chat_data, timeout=600)
    return render(request, 'messenger/messages.html', {'chat_data': chat_data, 'form': form})

def deletemessage(request, message_id):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    message = get_object_or_404(Message, pk=message_id)
    if message.is_deleted:
        return redirect('messages', chat_id=message.chat.id)
    message.is_deleted = True
    message.text = 'Сообщение удалено'
    message.picture = None
    message.save()
    cached_chat_data = cache.get(f"messages_{message.chat_id}")
    if cached_chat_data:
        cache.delete(f"messages_{message.chat_id}")
    return redirect('messages', chat_id=message.chat.id)


def usersview(request):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    users = CustomUser.objects.exclude(username=request.user.username)
    chats = Chats.objects.filter(Q(user_1=request.user.id) | Q(user_2=request.user.id))
    chats_with_users = {item: None for item in users}
    for chat in chats:
        for user in chats_with_users:
            if chat.user_1 == user or chat.user_2==user:
                chats_with_users[user] = chat
    return render(request, 'messenger/users.html', {"chats_with_users": chats_with_users})

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





