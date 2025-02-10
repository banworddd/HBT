from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('messenger.urls'), name='messenger'),
    path('groups/', include('groups.urls'), name='groups'),
    path('account/', include('users.urls'), name='account'),
    path('api/', include('api.urls'), name='api'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)