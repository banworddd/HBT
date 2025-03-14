from django.db.models import Q
from rest_framework import serializers
from django.conf import settings

from messenger.models import Chats, Message, MessageReaction
from users.models import CustomUser


class ChatDetailSerializer(serializers.ModelSerializer):
    messages_count = serializers.SerializerMethodField()

    class Meta:
        model = Chats
        fields = '__all__'

    def get_messages_count(self, obj):
        messages_count = Message.objects.filter(chat=obj).count()
        return messages_count


class ChatsSerializer(serializers.ModelSerializer):
    last_message_text = serializers.CharField(read_only=True)
    last_message_picture = serializers.SerializerMethodField()
    last_message_time = serializers.DateTimeField(read_only=True)
    last_message_status = serializers.CharField(read_only=True)
    last_message_author = serializers.CharField(read_only=True)
    username_1 = serializers.CharField(read_only=True)
    username_2 = serializers.CharField(read_only=True)
    public_name_1 = serializers.CharField(read_only=True)
    public_name_2 = serializers.CharField(read_only=True)
    chat_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Chats
        fields = [
            'id', 'user_1', 'user_2', 'username_1', 'username_2', 'public_name_1',
            'public_name_2', 'is_group', 'name', 'chat_avatar',
            'last_message_time', 'last_message_text', 'last_message_picture', 'last_message_status',
            'last_message_author'
        ]

    @staticmethod
    def get_chat_avatar(obj):
        if obj.is_group:
            return obj.avatar.url if obj.avatar else None
        return obj.user_2.avatar.url if obj.user_2 and obj.user_2.avatar else None

    @staticmethod
    def get_last_message_picture(obj):
        if obj.last_message_picture:
            return settings.MEDIA_URL + obj.last_message_picture
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            if instance.user_2 == request.user:
                representation['user_1'], representation['user_2'] = (
                    representation['user_2'], representation['user_1']
                )
                representation['username_1'], representation['username_2'] = (
                    representation['username_2'], representation['username_1']
                )
                representation['public_name_1'], representation['public_name_2'] = (
                    representation['public_name_2'], representation['public_name_1']
                )

        return representation


class MessageSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(read_only=True)
    author_avatar = serializers.CharField(read_only=True)
    author_username = serializers.CharField(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'text', 'chat', 'send_time', 'status',
            'picture', 'author_name', 'author_avatar', 'author_username'
        ]
        read_only_fields = ['author', 'send_time', 'status']
        extra_kwargs = {
            'text': {'required': False},
        }


class MessageReactionSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(read_only=True)
    author_avatar = serializers.CharField(read_only=True)
    author_username = serializers.CharField(read_only=True)
    class Meta:

        model = MessageReaction
        fields = ['id', 'reaction', 'author', 'time','message','author_avatar','author_name', 'author_username']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class MessageReactionsCountSerializer(serializers.ModelSerializer):
    reaction = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)
    user_reacted = serializers.BooleanField(read_only=True)
    user_reaction_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = MessageReaction
        fields = ['reaction', 'count', 'user_reacted', 'user_reaction_id']


class ContactsSerializer(serializers.ModelSerializer):
    chat_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ['username', 'avatar', 'public_name', 'chat_id']


class UserSerializer(serializers.ModelSerializer):
    is_contact = serializers.SerializerMethodField()
    chat_id = serializers.SerializerMethodField()
    last_chat_message_text = serializers.SerializerMethodField()
    last_chat_message_time = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'public_name',
            'avatar',
            'status',
            'is_contact',
            'chat_id',
            'last_chat_message_text',
            'last_chat_message_time'
        ]

    def get_is_contact(self, obj):
        request = self.context.get('request')
        if request.user.contacts.filter(username=obj.username).exists():
            return True
        return False

    def get_chat_id(self, obj):
        request = self.context.get('request')
        chat = Chats.objects.filter(
            Q(user_1=obj) & Q(user_2=request.user) |
            Q(user_1=request.user) & Q(user_2=obj)
        ).first()
        return chat.id if chat else None

    def get_last_chat_message_text(self, obj):
        chat_id = self.get_chat_id(obj)
        if chat_id:
            message = Message.objects.filter(chat__id=chat_id).last()
            return message.text if message else None

    def get_last_chat_message_time(self, obj):
        chat_id = self.get_chat_id(obj)
        if chat_id:
            message = Message.objects.filter(chat__id=chat_id).last()
            return message.send_time if message else None





