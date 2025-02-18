from django.urls import path
from .views import login_page, registration, profileview, logout_view, email_confirmation, edit_profile
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path ('login/', login_page, name='login'),
    path ('reg/', registration, name='reg'),
    path('logout/', logout_view, name='logout'),
    path('email_confirmation/', email_confirmation, name='emailconfirmation'),
    path('profile/', profileview, name='profile'),
    path('editprofile', edit_profile, name='edit_profile'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)