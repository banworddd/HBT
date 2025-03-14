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

    async def message_status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_status_update',
            'chat_id': event['chat_id'],
            'status': event['status'],
        }))

    async def receive(self, text_data):
        from .models import Message, Chats
        from users.models import CustomUser

        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')  # Добавляем тип сообщения

        if message_type == 'message_status_update':
            # Обработка обновления статуса сообщений
            chat_id = text_data_json['chat_id']
            status = text_data_json['status']

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_status_update',
                    'chat_id': chat_id,
                    'status': status,
                }
            )
            return

        # Обработка нового сообщения
        message_text = text_data_json.get('message')
        chat_id = text_data_json['chat_id']
        author_id = text_data_json['author_id']
        picture_url = text_data_json.get('picture_url')
        current_user = await sync_to_async(CustomUser.objects.get)(username=self.scope['user'])

        # Сохраняем сообщение в БД
        author = await sync_to_async(CustomUser.objects.get)(id=author_id)
        chat = await sync_to_async(Chats.objects.get)(id=chat_id)

        if chat.is_group:
            chat_avatar = chat.avatar.url
            chat_name = chat.name
            public_name_2 = None
            username_2 = None
        else:
            chat_name = None
            user_1 = await sync_to_async(CustomUser.objects.get)(id=chat.user_1_id)
            user_2 = await sync_to_async(CustomUser.objects.get)(id=chat.user_2_id)
            other_user = user_2 if user_1 == current_user else user_1
            chat_avatar = other_user.avatar.url
            username_2 = other_user.username
            public_name_2 = other_user.public_name

        new_message = await sync_to_async(Message.objects.create)(
            text=message_text,
            author=author,
            chat=chat,
            picture=picture_url if picture_url else None
        )

        # Отправляем сообщение в WebSocket с `id`
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'is_group': chat.is_group,
                'chat_avatar': chat_avatar,
                'chat_name': chat_name,
                'chat_id': new_message.chat.id,
                'username_2': username_2,
                'public_name_2': public_name_2,
                'id': new_message.id,
                'message': message_text,
                'author__username': author.username,
                'author_id': author.id,
                'send_time': new_message.send_time.isoformat(),
                'status': new_message.status,
                'is_deleted': new_message.is_deleted,
                'picture_url': new_message.picture.url if new_message.picture else None,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event, ensure_ascii=False))
