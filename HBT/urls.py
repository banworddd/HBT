from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('messenger.urls'), name='messenger'),
    path('account/', include('users.urls'), name='account'),
]
