from logging import raiseExceptions

from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

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

def messagesview(request, chat_id):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    chat = get_object_or_404(Chats, id=chat_id)
    messages = Message.objects.filter(chat=chat).order_by('send_time')
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            sender = request.user
            recipient = chat.user_2 if sender == chat.user_1 else chat.user_1
            text = form.cleaned_data['text']
            Message.objects.create(text = text, sender = sender, recipient = recipient, chat = chat)
            return redirect('messages', chat_id=chat.id)
        else:
            return raiseExceptions
    else:
        form = MessageForm()

    return render(request, 'messenger/messages.html', {
        "messages": messages,
        "current_user": request.user,
        "form" : form
    })

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





