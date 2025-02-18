from django.contrib.auth import  login
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .account_serializers import CustomUserSerializer, LoginSerializer
from .account_utils import code_generation


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response(
                {"detail": "Логин успешный"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            confirmation_code = code_generation(user.username)
            request.session['confirmation_code'] = confirmation_code

            return Response({"message": f"Пользователь зарегестрирован успешно"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class EmailConfirmationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_code = request.data.get('confirmation_code')

        if 'confirmation_code' not in request.session:
            return Response({"error": "В сессии нет кода подтверждения"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        if user_code == request.session['confirmation_code']:
            user.is_confirmed = True
            user.save()

            del request.session['confirmation_code']

            return Response({"message": "E-mail подтвержден успешно."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Неверный код подтверждения"}, status=status.HTTP_400_BAD_REQUEST)

