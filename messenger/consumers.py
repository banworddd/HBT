import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        from .models import Message, Chats  # Импорт внутрь метода
        from users.models import CustomUser

        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        chat_id = text_data_json['chat_id']
        author_id = text_data_json['author_id']

        # Сохраняем сообщение в базе данных
        author = await sync_to_async(CustomUser.objects.get)(id=author_id)
        chat = await sync_to_async(Chats.objects.get)(id=chat_id)
        new_message = await sync_to_async(Message.objects.create)(text=message, author=author, chat=chat)

        # Отправляем сообщение в группу
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'author__username': author.username,
                'send_time': new_message.send_time.isoformat(),
                'status': new_message.status,
                'is_deleted': new_message.is_deleted,
                'picture_url': new_message.picture.url if new_message.picture else None,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event, ensure_ascii=False))
