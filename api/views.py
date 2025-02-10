from django.db.models import Q
from rest_framework.generics import ListAPIView
from messenger.models import Chats
from users.models import CustomUser
from .serializers import ChatsSerializer

class ChatsListAPIView(ListAPIView):
    serializer_class = ChatsSerializer

    def get_queryset(self):
        user = self.request.query_params.get('user')
        if not user:
            return Chats.objects.none()

        if not user.startswith('@'):
            user = '@' + user

        user_obj = CustomUser.objects.filter(username=user).first()
        if not user_obj:
            return Chats.objects.none()

        queryset = Chats.objects.filter(
            (Q(user_1=user_obj) | Q(user_2=user_obj)) & Q(is_group=False) |
            (Q(is_group=True) & Q(users__username=user))
        ).order_by('-last_message_time')

        return queryset


