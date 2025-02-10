from django.urls import path
from .views import ChatsListAPIView

urlpatterns = [
    path('chats/', ChatsListAPIView.as_view(), name='chats-list'),
]