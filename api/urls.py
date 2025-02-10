from django.urls import path, include

urlpatterns = [
    path('', include('api.messenger_api_urls')),

]