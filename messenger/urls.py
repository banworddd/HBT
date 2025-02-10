from django.urls import path
from .views import startpage, chats_view, chat_detail_view, contactsview, create_chat_view, deletemessage, profileview, \
   deletecontact, create_group_chat, group_messages
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path ('', startpage, name='startpage'),
    path('contacts/', contactsview, name='contacts'),
    path('chats/', chats_view, name='chats'),
    path('chat/<int:chat_id>/', chat_detail_view, name='chat'),
    path('create_chat/<str:username>/', create_chat_view, name='create_chat'),
    path('deletemessage/<int:message_id>/', deletemessage, name='deletemessage'),
    path('profile/<str:username>/', profileview, name='profile'),
    path('deletecontact/<str:contact_name>/', deletecontact, name='deletecontact'),
    path('create_group_chat', create_group_chat, name = 'create_group_chat' ),
    path('group_messages/<int:chat_id>/', group_messages, name = 'group_messages' ),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
