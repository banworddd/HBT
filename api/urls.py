from django.urls import path, include

urlpatterns = [
    path('messenger/', include('api.messenger_api_urls')),
    path('account/', include('api.account_api_urls')),

]