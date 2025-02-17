from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, UpdateAPIView, \
    RetrieveDestroyAPIView, CreateAPIView
from rest_framework.response import Response

from messenger.models import Chats, Message, MessageReaction
from users.models import CustomUser
from .messenger_serializers import ChatsSerializer, MessageSerializer, MessageReactionSerializer, ContactsSerializer, \
    UserSerializer


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
        ).order_by('-last_messaging_time')

        for chat in queryset:
            if chat.user_1 == user_obj:
                pass
            if chat.user_2 == user_obj:
                chat.user_2 = chat.user_1
                chat.user_1 = user_obj

        return queryset


class ChatDetailAPIView(RetrieveAPIView):
    queryset = Chats.objects.all()
    serializer_class = ChatsSerializer
    lookup_field = 'pk'

class ChatCreateAPIView(CreateAPIView):
    queryset = Chats.objects.all()
    serializer_class = ChatsSerializer

    def perform_create(self, serializer):
        user_2 = serializer.validated_data['user_2']
        user_1 = serializer.validated_data['user_1']

        if not user_2 or not user_1:
            return Response('Переданы не все пользователи')

        serializer.save(user_1=user_1, user_2=user_2, is_group = False)
        return Response(serializer.data)

class ContactsChatDetailAPIView(RetrieveAPIView):
    serializer_class = ChatsSerializer

    def get(self, request, *args, **kwargs):
        user_id1 = self.kwargs.get('user_id1')
        user_id2 = self.kwargs.get('user_id2')
        try:
            user_1_obj = CustomUser.objects.filter(id=user_id1).first()
            user_2_obj = CustomUser.objects.filter(id=user_id2).first()

        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Объект не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            chat = Chats.objects.filter(
                (Q(user_1=user_1_obj) & Q(user_2=user_2_obj)) | (Q(user_1=user_2_obj) & Q(user_2=user_1_obj))).first()

            if chat is None:
                return Response(
                    {"error": "Чата не существует"},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(self.get_serializer(chat).data)

        except Chats.DoesNotExist:
            return Response(
                {"error": "Чата не существует"},
                status=status.HTTP_404_NOT_FOUND
            )


class ContactsAPIView(RetrieveAPIView):

    queryset = CustomUser.objects.all()
    serializer_class = ContactsSerializer

    def get_object(self):
        id = self.kwargs.get('pk')
        user_obj = CustomUser.objects.filter(id=id).first()
        if not user_obj:
            return Response({"error": "Пользователя не существует"}, status=status.HTTP_404_NOT_FOUND)
        return user_obj

    def get(self, request, *args, **kwargs):
        user_obj = self.get_object()

        if isinstance(user_obj, Response):
            return user_obj

        return Response(self.get_serializer(user_obj).data)

class UpdateContactsAPIView(UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ContactsSerializer
    lookup_field = 'pk'

    def perform_update(self, serializer):
        id = self.kwargs.get('pk')
        user_obj = CustomUser.objects.filter(id=id).first()

        if not user_obj:
            return Response({"error": "Пользователя не существует"},
                            status=status.HTTP_404_NOT_FOUND)

        contact = serializer.validated_data['contacts']
        contact_obj = CustomUser.objects.filter(username = contact).first()

        if not contact_obj:
            return Response({"error": "Контакта не существует"},
                            status=status.HTTP_404_NOT_FOUND)

        contacts = user_obj.contacts

        for _ in range(len(contacts)):
            if contacts[_] == contact:
                contacts.remove(contact)
                serializer.save(contacts = contacts)
                return Response ('Пользователь удален из контактов ')

        contacts.append(contact)
        serializer.save(user=user_obj, contacts=contacts)
        return Response('Пользователь добавлен в контакты')


class UsersSearchAPIView(ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.query_params.get('user')
        user_obj = self.request.user

        if not user:
            return CustomUser.objects.none()

        queryset = CustomUser.objects.filter(username__icontains=user).order_by('username')
        for _ in queryset:
            if _.username in user_obj.contacts:
                _.is_contact = True
            else:
                _.is_contact = False
            if Chats.objects.filter(Q(user_1=user_obj)& Q(user_2=_) | Q(user_2=user_obj)& Q(user_1=_)).exists():
                _.is_chat = True
                _.chat_id = Chats.objects.filter(Q(user_1=user_obj)& Q(user_2=_) | Q(user_2=user_obj)& Q(user_1=_)).first().id
                _.last_chat_message_text = Message.objects.filter(chat_id = _.chat_id).last().text if Message.objects.filter(chat_id = _.chat_id).exists() else None
                _.last_chat_message_time = Message.objects.filter(chat_id = _.chat_id).last().send_time if Message.objects.filter(chat_id = _.chat_id).exists() else None
            else:
                _.is_chat = False
                _.chat_id = None

        return queryset

class UserProfileAPIView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    def get_object(self):
        username = self.kwargs.get('username')
        request_user = self.request.user

        if not username.startswith('@'):
            username = '@' + username

        user_obj = CustomUser.objects.filter(username=username).first()

        if not user_obj:
            return Response({"error": "Пользователя не существует"},
                            status=status.HTTP_404_NOT_FOUND)

        if user_obj.username in request_user.contacts:
            user_obj.is_contact = True
        else:
            user_obj.is_contact = False

        if Chats.objects.filter(Q(user_1=user_obj) & Q(user_2=request_user) | Q(user_2=user_obj) & Q(user_1=request_user)).exists():
            user_obj.is_chat = True
            user_obj.chat_id = Chats.objects.filter(
                Q(user_1=user_obj) & Q(user_2=request_user) | Q(user_2=user_obj) & Q(user_1=request_user)).first().id
            user_obj.last_chat_message_text = Message.objects.filter(chat_id=user_obj.chat_id).last().text if Message.objects.filter(
                chat_id=user_obj.chat_id).exists() else None
            user_obj.last_chat_message_time = Message.objects.filter(
                chat_id=user_obj.chat_id).last().send_time if Message.objects.filter(chat_id=user_obj.chat_id).exists() else None

        return user_obj


    def get(self, request, *args, **kwargs):
        user_obj = self.get_object()

        if isinstance(user_obj, Response):
            return user_obj

        return Response(self.get_serializer(user_obj).data)


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

    def perform_update(self, serializer):
        message = self.get_object()
        if message.author == self.request.user or self.request.user.is_superuser:
            serializer.save(is_edited=True)
        else:
            raise PermissionDenied('Вы не можете редактировать это сообщение')

class MessageReactionAPIView(ListCreateAPIView):
    serializer_class = MessageReactionSerializer

    def get_queryset(self):
        message_id = self.request.query_params.get('message_id')

        if not message_id:
            return MessageReaction.objects.none()

        message_obj = Message.objects.filter(id=message_id).first()

        if not message_obj:
            return MessageReaction.objects.none()

        queryset = MessageReaction.objects.filter(message=message_obj)
        return queryset


class MessageReactionDetailAPIView(RetrieveDestroyAPIView):
    queryset = MessageReaction.objects.all()
    serializer_class = MessageReactionSerializer
    lookup_field = 'pk'


























