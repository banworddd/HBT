
from django.urls import path
from .views import startpage, groups, user_subcriptions, group, subscribe, unsubscribe, creategroup, postview, deletepost, editpost, editgroup
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path ('', startpage, name='startpage'),
    path('groups/', groups, name='groups'),
    path('user_subs/', user_subcriptions, name='user_subs'),
    path('group/<str:group_name>/', group, name='group'),
    path('group/<str:group_name>/subscribe/', subscribe, name='subscribe'),
    path('group/<str:group_name>/unsubscribe/', unsubscribe, name='unsubscribe'),
    path('create_group/', creategroup, name='create_group'),
    path('post/<slug:post_slug>/', postview, name='post' ),
    path('deletepost/<slug:post_slug>/', deletepost, name='deletepost'),
    path('editpost/<slug:post_slug>/', editpost, name='editpost'),
    path('editgroup/<str:group_name>/', editgroup, name='editgroup'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
