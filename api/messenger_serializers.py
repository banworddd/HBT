from rest_framework import serializers
from messenger.models import Chats, Message

class ChatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chats
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'text', 'chat', 'send_time', 'status', 'picture', 'author_name']

        read_only_fields = ['author', 'send_time', 'status']

    def get_author_name(self, obj):
        return obj.author.username  # Предполагается, что у модели User есть поле username


