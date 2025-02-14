from django.db.models import Q
from rest_framework import serializers
from messenger.models import Chats, Message, MessageReaction
from users.models import CustomUser

class ChatsSerializer(serializers.ModelSerializer):
    last_message_text = serializers.SerializerMethodField()
    last_message_picture = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    username1 = serializers.SerializerMethodField()
    username2 = serializers.SerializerMethodField()

    class Meta:
        model = Chats
        fields = ['id','user_1', 'user_2','username1','username2', 'is_group', 'users','admins','name','avatar','last_message_time', 'last_message_text', 'last_message_picture']

    def get_last_message_text(self, obj):
        try:
            message = Message.objects.filter(chat = obj).last()
            return message.text
        except:
            return None

    def get_last_message_picture(self, obj):
        try:
            message = Message.objects.filter(chat = obj).last()
            return message.picture.url
        except:
            return None

    def get_last_message_time(self, obj):
        try:
            message = Message.objects.filter(chat=obj).last()
            return message.send_time
        except:
            return None

    def get_username1(self, obj):
        try:
            user_obj = CustomUser.objects.get(pk=obj.user_1.id)
            return user_obj.username
        except:
            return None

    def get_username2(self, obj):
        try:
            user_obj = CustomUser.objects.get(pk=obj.user_2.id)
            return user_obj.username
        except:
            return None


class MessageSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'text', 'chat', 'send_time', 'status', 'picture', 'author_name', 'author_avatar']
        read_only_fields = ['author', 'send_time', 'status']

    def get_author_name(self, obj):
        return obj.author.username

    def get_author_avatar(self, obj):
        return obj.author.avatar.url if obj.author.avatar else None


class MessageReactionSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_avatar = serializers.SerializerMethodField()
    message_text = serializers.SerializerMethodField()

    class Meta:
        model = MessageReaction
        fields = ['id', 'author','author_avatar','author_name', 'reaction', 'reaction_time','message_text','message']

    def get_author_name(self, obj):
        return obj.author.username

    def get_author_avatar(self, obj):
        return obj.author.avatar.url if obj.author.avatar else None

    def get_message_text(self, obj):
        return obj.message.text if obj.message else None


class ContactsSerializer(serializers.ModelSerializer):
    chat_id = serializers.SerializerMethodField()
    contact_ids = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['contacts','contact_ids', 'chat_id']

    def get_chat_id(self, obj):
        chat_ids = []
        for contact in obj.contacts:
            contact_obj = CustomUser.objects.get(username=contact)
            try:
                chat = Chats.objects.get((Q(user_1 = contact_obj) & Q(user_2 = obj) )| (Q(user_1 = obj) & Q(user_2 = contact_obj)))
                chat_ids.append(chat.id)
            except:
                chat_ids.append(None)
        return chat_ids

    def get_contact_ids(self, obj):
        contact_ids = []
        for contact in obj.contacts:
            contact_obj = CustomUser.objects.get(username=contact)
            contact_ids.append(contact_obj.id)
        return contact_ids



