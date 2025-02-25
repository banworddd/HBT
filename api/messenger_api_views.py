from django.db.models import Q,F, OuterRef, Count, Case, When, Value, BooleanField,IntegerField
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    ListCreateAPIView,
    UpdateAPIView,
    RetrieveDestroyAPIView,
    CreateAPIView,
    RetrieveUpdateAPIView, get_object_or_404
)
from rest_framework.response import Response

from messenger.models import Chats, Message, MessageReaction
from users.models import CustomUser
from .messenger_serializers import (
    ChatsSerializer,
    MessageSerializer,
    MessageReactionSerializer,
    ContactsSerializer,
    UserSerializer,
MessageReactionsCountSerializer
)


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
        )

        last_message_subquery = Message.objects.filter(
            chat=OuterRef('pk')
        ).order_by('-send_time').values('text', 'send_time', 'picture')[:1]

        user_1_subquery = CustomUser.objects.filter(
            pk=OuterRef('user_1__id')
        ).values('username', 'public_name')

        user_2_subquery = CustomUser.objects.filter(
            pk=OuterRef('user_2__id')
        ).values('username', 'public_name')

        queryset = queryset.annotate(
            last_message_text=last_message_subquery.values('text'),
            last_message_time=last_message_subquery.values('send_time'),
            last_message_picture=last_message_subquery.values('picture'),
            username_1=user_1_subquery.values('username'),
            public_name_1=user_1_subquery.values('public_name'),
            username_2=user_2_subquery.values('username'),
            public_name_2=user_2_subquery.values('public_name')
        )

        return queryset.order_by('-last_message_time')


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


class ChatsSearchAPIView(ListAPIView):
    serializer_class = ChatsSerializer

    def get_queryset(self):
        search_query = self.request.query_params.get('search_query')
        if not search_query:
            return Chats.objects.none()

        request_user = self.request.user
        queryset = Chats.objects.filter(
            (Q(user_1__username__icontains=search_query) &
             Q(user_2__username=request_user.username)) |
            (Q(user_2__username__icontains=search_query) &
             Q(user_1__username=request_user.username)) |
            (Q(is_group=True) & Q(name__icontains=search_query))
        )

        last_message_subquery = Message.objects.filter(
            chat=OuterRef('pk')
        ).order_by('-send_time').values('text', 'send_time', 'picture')[:1]

        user_1_subquery = CustomUser.objects.filter(
            pk=OuterRef('user_1__id')
        ).values('username', 'public_name')

        user_2_subquery = CustomUser.objects.filter(
            pk=OuterRef('user_2__id')
        ).values('username', 'public_name')

        queryset = queryset.annotate(
            last_message_text=last_message_subquery.values('text'),
            last_message_time=last_message_subquery.values('send_time'),
            last_message_picture=last_message_subquery.values('picture'),
            username_1=user_1_subquery.values('username'),
            public_name_1=user_1_subquery.values('public_name'),
            username_2=user_2_subquery.values('username'),
            public_name_2=user_2_subquery.values('public_name')
        )

        return queryset.order_by('-last_message_time')


class GroupChatCreateAPIView(CreateAPIView):
    queryset = Chats.objects.all()
    serializer_class = ChatsSerializer

    def perform_create(self ,serializer):
        request_user = self.request.user

        users = serializer.validated_data['users']
        admins = serializer.validated_data['admins']
        name = serializer.validated_data['name']

        users_set = CustomUser.objects.filter(Q(username__in=users) | Q(username=request_user.username)).distinct()
        admins_set = CustomUser.objects.filter(Q(username__in=admins) | Q(username=request_user.username)).distinct()

        serializer.save(is_group = True, admins = admins_set, users = users_set, name = name)
        return Response(serializer.data)


class GroupChatUpdateAPIView(RetrieveUpdateAPIView):

    queryset = Chats.objects.all()
    serializer_class = ChatsSerializer
    lookup_field = 'pk'

    def perform_update(self, serializer):
        users = serializer.validated_data['users']
        chat_object = self.get_object()
        users_now = chat_object.users.all()
        users_set = CustomUser.objects.filter(Q(username__in=users_now) | Q(username__in = users))


        name = serializer.validated_data['name']
        if not name:
            name = chat_object.name

        try:
            admins = serializer.validated_data['admins']
        except:
            admins = chat_object.admins.all()

        serializer.save(is_group = True, admins = admins, users = users_set, name = name)


class ContactsAPIView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ContactsSerializer
    lookup_field = 'pk'


class UpdateContactsAPIView(UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ContactsSerializer
    lookup_field = 'pk'

    def perform_update(self, serializer):
        user_obj = CustomUser.objects.get(pk=self.kwargs.get('pk'))
        new_contacts = serializer.validated_data['contacts']
        contacts = user_obj.contacts.all()
        queryset = CustomUser.objects.filter(Q(pk__in = contacts) | Q(username__in = new_contacts)).distinct()
        user_obj.contacts.set(queryset)
        user_obj.save()


class UsersSearchAPIView(ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.query_params.get('user')
        if not user:
            return CustomUser.objects.none()
        queryset = CustomUser.objects.filter(Q(username__icontains=user)| Q(public_name__icontains=user)).order_by('username').exclude(username = self.request.user.username)

        return queryset


class UserProfileAPIView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    def get_object(self):
        username = self.kwargs.get('username')

        if not username.startswith('@'):
            username = '@' + username

        user_obj = CustomUser.objects.filter(username=username).first()

        if not user_obj:
            return Response({"error": "Пользователя не существует"},
                            status=status.HTTP_404_NOT_FOUND)

        return user_obj

    def get(self, request, *args, **kwargs):
        user_obj = self.get_object()

        if isinstance(user_obj, Response):
            return user_obj

        return Response(self.get_serializer(user_obj).data)


class MessagePagination(PageNumberPagination):
    page_size = 20  # Количество сообщений на странице
    page_size_query_param = 'page_size'
    max_page_size = 100


class MessagesCreateListAPIView(ListCreateAPIView):
    serializer_class = MessageSerializer
    pagination_class = MessagePagination

    def get_queryset(self):
        chat_id = self.request.query_params.get('chat_id')

        if not chat_id:
            return Message.objects.none()

        # Проверка существования чата
        chat_obj = Chats.objects.filter(id=chat_id).first()
        if not chat_obj:
            return Message.objects.none()

        # Получаем сообщения
        queryset = Message.objects.filter(chat=chat_obj, is_deleted=False).order_by('send_time')

        # Обновляем статус сообщений всех, кроме текущего пользователя
        Message.objects.filter(
            chat=chat_obj,
            is_deleted=False,

            status='S'
        ).exclude(author=self.request.user).update(status='R')
        author_subquery = CustomUser.objects.filter(pk = OuterRef('author__id')).values('public_name','avatar', 'username')
        queryset = queryset.annotate(author_name = author_subquery.values('public_name'), author_avatar = author_subquery.values('avatar'), author_username = author_subquery.values('username'))
        return queryset

    def perform_create(self, serializer):
        chat_id = self.request.query_params.get('chat_id')
        # Проверка существования чата
        chat_obj = Chats.objects.filter(id=chat_id).first()
        if not chat_obj:
            return Response({'error': 'Чат не найден.'}, status=status.HTTP_404_NOT_FOUND)

        serializer.save(author=self.request.user, chat=chat_obj)

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
            return Response({"error": "message_id parameter is required"}, status=400)

        queryset = MessageReaction.objects.filter(message__id=message_id)
        author_subquery = CustomUser.objects.filter(pk=OuterRef('author__id')).values(
            'public_name', 'avatar', 'username'
        )
        queryset = queryset.annotate(
            author_name=author_subquery.values('public_name'),
            author_username=author_subquery.values('username'),
            author_avatar=author_subquery.values('avatar')
        )

        return queryset

class MessageReactionsCountAPIView(ListAPIView):
    serializer_class = MessageReactionsCountSerializer

    def get_queryset(self):
        message_id = self.request.query_params.get('message_id')
        request_user_id = self.request.user.id

        if not message_id:
            raise NotFound("message_id parameter is required")

        queryset = MessageReaction.objects.filter(message__id=message_id).values('reaction').distinct().annotate(
            count=Count('reaction'),
            user_reacted=Case(
                When(author__id=request_user_id, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ), user_reaction_id = Case(
                When(author__id=request_user_id, then=F('id')),
                default=Value(None),
                output_field=IntegerField()
        )
        )

        return queryset

class MessageReactionCreateAPIView(CreateAPIView):
    queryset = MessageReaction.objects.all()
    serializer_class = MessageReactionSerializer

    def perform_create(self, serializer):
        message_id = self.request.query_params.get('message_id')
        message_obj = get_object_or_404(Message, id=message_id)
        serializer.save(message=message_obj)


class MessageReactionDetailAPIView(RetrieveDestroyAPIView):
    queryset = MessageReaction.objects.all()
    serializer_class = MessageReactionSerializer
    lookup_field = 'pk'


























