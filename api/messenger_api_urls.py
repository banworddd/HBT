from django.urls import path
from .messenger_api_views import ChatsListAPIView, ChatDetailAPIView, MessagesListAPIView, MessageDetailAPIView


urlpatterns = [
    path('chats/', ChatsListAPIView.as_view(), name='chats-list'),
    path('chat_info/<int:pk>/', ChatDetailAPIView.as_view(), name='chat-detail'),
    path('chat_messages_list/', MessagesListAPIView.as_view(), name='chat-messages-list'),
    path('message_info/<int:pk>/', MessageDetailAPIView.as_view(), name='message-detail'),
]
