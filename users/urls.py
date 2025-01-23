from django.contrib import admin
from django.urls import path
from .views import login_view, registration, profileview, chatsview, messagesview, usersview, logout_view, email_confirmation
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path ('login/', login_view, name='login'),
    path ('reg/', registration, name='reg'),
    path('profile/<str:username>/', profileview, name='profile'),
    path('chats/<str:username>/', chatsview, name='chats' ),
    path('messages/<int:chat_id>/', messagesview, name='messages'),
    path('users/', usersview, name='users'),
    path('logout/', logout_view, name='logout'),
    path('email_confrimation/', email_confirmation, name='emailconfirmation'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)