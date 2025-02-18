from django.urls import path
from .account_api_views import (
    LoginView,
    RegistrationView,
    EmailConfirmationView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegistrationView.as_view(), name='register'),
    path(
        'confirm_email/',
        EmailConfirmationView.as_view(),
        name='email_confirmation',
    ),
]