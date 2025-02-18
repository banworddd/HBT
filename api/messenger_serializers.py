from django.db.models import Q
from rest_framework import serializers

from messenger.models import Chats, Message, MessageReaction
from users.models import CustomUser

class ChatsSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, queryset=CustomUser.objects.all())
    admins = serializers.PrimaryKeyRelatedField(many=True, queryset=CustomUser.objects.all())
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            if instance.user_2 == request.user:
                representation['user_1'], representation['user_2'] = representation['user_2'], representation['user_1']
                representation['username1'], representation['username2'] = representation['username2'], representation[
                    'username1']

        return representation


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
    contacts_usernames = serializers.SerializerMethodField()
    contacts_chats = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['contacts', 'contacts_usernames', 'contacts_chats']

    def get_contacts_usernames(self, obj):
        queryset = obj.contacts.all()
        return queryset.values_list('username', flat=True)

    def get_contacts_chats(self, obj):
        queryset = obj.contacts.all()
        chats_queryset = Chats.objects.filter(Q(user_1__in = queryset) & Q(user_2 = obj) | Q(user_2__in = queryset) & Q(user_1 = obj))
        return chats_queryset.values_list('id', flat=True)





class UserSerializer(serializers.ModelSerializer):
    is_contact = serializers.SerializerMethodField()
    is_chat = serializers.SerializerMethodField()
    chat_id = serializers.SerializerMethodField()
    last_chat_message_text = serializers.SerializerMethodField()
    last_chat_message_time = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['username', 'public_name', 'avatar', 'status','is_contact', 'is_chat', 'chat_id', 'last_chat_message_text', 'last_chat_message_time']

    def get_is_contact(self, obj):
        try:
            return obj.is_contact
        except:
            return None

    def get_is_chat(self,obj):
        try:
            return obj.is_chat
        except:
            return None

    def get_chat_id(self,obj):
        try:
            return obj.last_chat_id
        except:
            return None

    def get_last_chat_message_text(self, obj):
        try:
            return obj.last_chat_message_text
        except:
            return None

    def get_last_chat_message_time(self, obj):
        try:
            return obj.last_chat_message_time
        except:
            return None






