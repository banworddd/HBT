from django.urls import path
from .views import startpage, chatsview, messagesview, usersview, create_chat_view
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path ('', startpage, name='startpage'),
    path('users/', usersview, name='users'),
    path('chats/<str:username>/', chatsview, name='chats' ),
    path('messages/<int:chat_id>/', messagesview, name='messages'),
    path('create_chat/<str:username>/', create_chat_view, name='create_chat'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
