from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache

from common.utils import check_user_status, check_user_session, check_active_sessions
from users.models import CustomUser

from .forms import MessageForm, GroupChatForm
from .models import Chats, Message, MessageReaction

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
    group_chats = Chats.objects.filter(users = user)

    messages_dict = {}
    for chat in chats:
        other_user = chat.user_2 if chat.user_1.id == user_id else chat.user_1
        last_message = Message.objects.filter(chat=chat).last()
        messages_dict[other_user] = {
            'chat_id': chat.id,
            'message': last_message.text if last_message else None
        }

    return render(request, 'messenger/chats.html', {'username': username, 'messages': messages_dict, 'group_chats': group_chats})

def messagesview(request, chat_id):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    chat = get_object_or_404(Chats, id=chat_id)

    messages = Message.objects.filter(chat=chat).select_related('author', 'chat').order_by('send_time')
    other_user = chat.user_1 if chat.user_2 == request.user else chat.user_2
    other_user_status = check_user_session(request, other_user.id)
    messages_reactions = MessageReaction.objects.filter(message__chat = chat)
    user_reactions = {reaction.message_id: reaction.status for reaction in messages_reactions.filter(react_user=request.user)}

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
                        'reactions': messages_reactions.filter(message = msg)
                    }
                    for msg in messages
                ],
                "other_user": other_user.username,
                "other_user_status": other_user_status,
                "current_user": request.user.username,
                "chat_id": chat_id,
                'user_reactions': user_reactions,
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
                'reactions': messages_reactions.filter(message=msg),
            }
            for msg in messages
        ],
        "other_user": other_user.username,
        "other_user_status": other_user_status,
        "current_user": request.user.username,
        "chat_id": chat_id,
        'user_reactions': user_reactions,
    }
    cache.set(f"messages_{chat_id}_{request.user.id}", chat_data, timeout=600)
    return render(request, 'messenger/messages.html', {'chat_data': chat_data, 'form': form})

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

def sendreaction(request, message_id, reaction):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response
    message = get_object_or_404(Message, pk=message_id)
    cache.delete(f"messages_{message.chat.id}_{request.user.id}")
    reaction_exists = MessageReaction.objects.filter(message=message, react_user=request.user).exists()
    if reaction_exists:
        reaction_exists = MessageReaction.objects.get(message=message, react_user=request.user)
        if reaction_exists.status == reaction:
            reaction_exists.delete()
            return redirect('messages', chat_id=message.chat.id)
        else:
            reaction_exists.delete()
            new_reaction = MessageReaction.objects.create(message=message, react_user=request.user, status=reaction)
            new_reaction.save()
            return redirect('messages', chat_id=message.chat.id)
    else:
        new_reaction = MessageReaction.objects.create(message=message, react_user=request.user, status=reaction)
        new_reaction.save()
        return redirect('messages', chat_id=message.chat.id)




def contactsview(request):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    user = get_object_or_404(CustomUser, pk=request.user.id)
    contacts = {}
    for contact in user.contacts:
        contact_user = get_object_or_404(CustomUser, username = contact)
        if Chats.objects.filter(Q(user_1 = request.user) & Q(user_2 = contact_user) | Q(user_2 = request.user) & Q(user_1 = contact_user)).exists():
            contacts[contact_user] = Chats.objects.get(Q(user_1 = request.user) & Q(user_2 = contact_user) | Q(user_2 = request.user) & Q(user_1 = contact_user))
        else:
            contacts[contact_user] = None

    return render(request, 'messenger/contacts.html', {'contacts': contacts})

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










