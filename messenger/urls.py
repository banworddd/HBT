from django.urls import path
from .views import startpage, chatsview, messagesview, contactsview, create_chat_view, deletemessage, profileview, \
    sendreaction, deletecontact, create_group_chat
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path ('', startpage, name='startpage'),
    path('contacts/', contactsview, name='contacts'),
    path('chats/<str:username>/', chatsview, name='chats' ),
    path('messages/<int:chat_id>/', messagesview, name='messages'),
    path('create_chat/<str:username>/', create_chat_view, name='create_chat'),
    path('deletemessage/<int:message_id>/', deletemessage, name='deletemessage'),
    path('profile/<str:username>/', profileview, name='profile'),
    path('sendreaction/<int:message_id>/<str:reaction>/',sendreaction, name='sendreaction' ),
    path('deletecontact/<str:contact_name>/', deletecontact, name='deletecontact'),
    path('create_group_chat', create_group_chat, name = 'create_group_chat' ),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
