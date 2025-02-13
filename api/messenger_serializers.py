from django.db.models import Q
from rest_framework import serializers
from messenger.models import Chats, Message, MessageReaction
from users.models import CustomUser

class ChatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chats
        fields = '__all__'

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chats
        fields = ['user_1', 'user_2']

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
            print(contact_obj, obj)
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



