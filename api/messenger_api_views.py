from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, UpdateAPIView

from messenger.models import Chats, Message
from users.models import CustomUser
from .messenger_serializers import ChatsSerializer, MessageSerializer

class ChatsListAPIView(ListAPIView):
    serializer_class = ChatsSerializer

    def get_queryset(self):
        user = self.request.query_params.get('user')
        if not user:
            return Chats.objects.none()

        if not user.startswith('@'):
            user = '@' + user

        user_obj = CustomUser.objects.filter(username=user).first()
        if not user_obj:
            return Chats.objects.none()

        queryset = Chats.objects.filter(
            (Q(user_1=user_obj) | Q(user_2=user_obj)) & Q(is_group=False) |
            (Q(is_group=True) & Q(users__username=user))
        ).order_by('-last_message_time')

        return queryset


class ChatDetailAPIView(RetrieveAPIView):
    queryset = Chats.objects.all()
    serializer_class = ChatsSerializer
    lookup_field = 'pk'

class MessagesCreateListAPIView(ListCreateAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_id = self.request.query_params.get('chat_id')

        if not chat_id:
            return Chats.objects.none()

        chat_obj = Chats.objects.filter(id=chat_id).first()
        if not chat_obj:
            return Chats.objects.none()

        queryset = Message.objects.filter(chat=chat_obj, is_deleted=False).order_by('send_time')

        for msg in queryset.reverse():
            if msg.author == self.request.user:
                break
            else:
                msg.status = 'R'
                msg.save()

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class MessageDeleteAPIView(UpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'pk'

    def perform_update(self, serializer):
        message = self.get_object()
        if message.author == self.request.user or self.request.user.is_superuser:
            serializer.save(is_deleted=True, text=message.text ,picture=None)
        else:
            raise PermissionDenied('Вы не можете удалить это сообщение')

class MessageUpdateAPIView(UpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'pk'



















