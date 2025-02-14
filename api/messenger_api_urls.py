from django.urls import path
from .messenger_api_views import ChatsListAPIView, ChatDetailAPIView, MessagesCreateListAPIView, MessageDeleteAPIView, \
    MessageUpdateAPIView, MessageReactionAPIView, MessageReactionDetailAPIView, ContactsChatDetailAPIView, \
    ContactsAPIView, ChatCreateAPIView, UpdateContactsAPIView

urlpatterns = [
    path('chats/', ChatsListAPIView.as_view(), name='chats-list'),
    path('chat_info/<int:pk>/', ChatDetailAPIView.as_view(), name='chat-detail'),
    path('chat_create/', ChatCreateAPIView.as_view(), name='chat-create'),
    path('contacts/<int:pk>/', ContactsAPIView.as_view(), name='contacts-chat-detail'),
    path('add_contact/<int:pk>/', UpdateContactsAPIView.as_view(), name='add-contact'),
    path('contacts_chat_detail/<int:user_id1>/<int:user_id2>/', ContactsChatDetailAPIView.as_view(), name='contacts-chat-detail'),
    path('chat_messages_list/', MessagesCreateListAPIView.as_view(), name='chat-messages-list'),
    path('chat_message_delete/<int:pk>/', MessageDeleteAPIView.as_view(), name='chat-message-delete'),
    path('chat_message_update/<int:pk>/', MessageUpdateAPIView.as_view(), name='chat-message-update'),
    path('message_reactions/', MessageReactionAPIView.as_view(), name='message-reactions'),
    path('message_reactions_detail/<int:pk>/', MessageReactionDetailAPIView.as_view(), name='message-reactions-detail'),
]
