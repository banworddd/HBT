from django.urls import path
from .views import startpage, chats_view, chat_detail_view, contactsview, profileview, create_group_chat
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path ('', startpage, name='startpage'),
    path('contacts/', contactsview, name='contacts'),
    path('chats/', chats_view, name='chats'),
    path('chat/<int:chat_id>/', chat_detail_view, name='chat'),
    path('profile/<str:username>/', profileview, name='profile'),
    path('create_group_chat', create_group_chat, name = 'create_group_chat' ),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
