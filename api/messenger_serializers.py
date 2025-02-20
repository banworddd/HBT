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
    public_name1 = serializers.SerializerMethodField()
    public_name2 = serializers.SerializerMethodField()
    chat_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Chats
        fields = ['id','user_1', 'user_2', 'username1', 'username2', 'public_name1', 'public_name2', 'is_group', 'users', 'admins', 'name', 'chat_avatar', 'last_message_time', 'last_message_text', 'last_message_picture']

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

    def get_public_name1(self, obj):
        try:
            user_obj = CustomUser.objects.get(pk=obj.user_1.id)
            return user_obj.public_name
        except:
            return None

    def get_public_name2(self, obj):
        try:
            user_obj = CustomUser.objects.get(pk=obj.user_2.id)
            return user_obj.public_name
        except:
            return None

    def get_chat_avatar(self, obj):
        if obj.is_group:
            return obj.avatar.url if obj.avatar else None
        else:
            return obj.user_2.avatar.url if obj.user_2.avatar else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.user.is_authenticated:
            if instance.user_2 == request.user:
                representation['user_1'], representation['user_2'] = representation['user_2'], representation['user_1']
                representation['username1'], representation['username2'] = representation['username2'], representation[
                    'username1']
                representation['public_name1'], representation['public_name2'] = representation['public_name2'], representation[
                    'public_name1']

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
    chat_id = serializers.SerializerMethodField()
    last_chat_message_text = serializers.SerializerMethodField()
    last_chat_message_time = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['username', 'public_name', 'avatar', 'status','is_contact', 'chat_id', 'last_chat_message_text', 'last_chat_message_time']

    def get_is_contact(self, obj):
        request = self.context.get('request')
        if request.user.contacts.filter(username=obj.username).exists():
            return True
        else:
            return False

    def get_chat_id(self, obj):
        request = self.context.get('request')
        return Chats.objects.filter(
                Q(user_1=obj) & Q(user_2=request.user) | Q(user_1=request.user) & Q(user_2=obj)).first().id if  Chats.objects.filter(
                Q(user_1=obj) & Q(user_2=request.user) | Q(user_1=request.user) & Q(user_2=obj)).exists() else None

    def get_last_chat_message_text(self, obj):
        request = self.context.get('request')
        chat_id = self.get_chat_id(obj)
        if chat_id:
            return Message.objects.filter(chat__id = chat_id ).last().text if Message.objects.filter(chat__id = chat_id).exists() else None

    def get_last_chat_message_time(self, obj):
        request = self.context.get('request')

        chat_id = self.get_chat_id(obj)
        if chat_id:
            return Message.objects.filter(chat__id=chat_id).last().send_time if Message.objects.filter(
                chat__id=chat_id).exists() else None




