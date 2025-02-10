from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveAPIView
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


class MessagesListAPIView(ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_id = self.request.query_params.get('chat_id')

        if not chat_id:
            return Chats.objects.none()

        chat_obj = Chats.objects.filter(id=chat_id).first()
        if not chat_obj:
            return Chats.objects.none()

        queryset = Message.objects.filter(chat=chat_obj).order_by('-send_time')

        return queryset

class MessageDetailAPIView(RetrieveAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'pk'






