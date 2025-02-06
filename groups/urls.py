from django.urls import path
from .views import groups, user_subcriptions, group, subscribe, unsubscribe, creategroup, postview, deletepost, editpost, editgroup, sendreaction, commentreaction
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', groups, name='groups'),
    path('subs/', user_subcriptions, name='user_subs'),
    path('create_group/', creategroup, name='create_group'),
    path('<str:group_name>/', group, name='group'),
    path('<str:group_name>/subscribe/', subscribe, name='subscribe'),
    path('<str:group_name>/unsubscribe/', unsubscribe, name='unsubscribe'),
    path('post/<slug:post_slug>/', postview, name='post' ),
    path('deletepost/<slug:post_slug>/', deletepost, name='deletepost'),
    path('editpost/<slug:post_slug>/', editpost, name='editpost'),
    path('addpostreaction/<slug:post_slug>/<str:reaction>/',sendreaction, name='postreaction' ),
    path('editgroup/<str:group_name>/', editgroup, name='editgroup'),
    path('sendcommentreaction/<int:comment_id>/<str:reaction>/', commentreaction, name='commentreaction' ),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
