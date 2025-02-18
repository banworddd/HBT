from django.contrib.auth import authenticate, login
from .account_serializers import LoginSerializer, CustomUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .account_utils import code_generation
from users.models import CustomUser, ConfirmationCode


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                if not user.is_confirmed:
                    return Response(
                        {'detail': 'Email is not confirmed.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                login(request, user)
                return Response(
                    {'detail': 'Login successful.'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'detail': 'Invalid username or password'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
                login(request, user)
                confirmation_code = code_generation(user.username)

                # Сохраняем код подтверждения в сессии
                request.session['confirmation_code'] = confirmation_code

                print(f"Confirmation code for {user.username}: {confirmation_code}")  # Выводим в консоль для отладки

                return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": "An error occurred while creating the user."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class EmailConfirmationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_code = request.data.get('confirmation_code')

        # Проверка, есть ли код подтверждения в сессии
        if 'confirmation_code' not in request.session:
            return Response({"error": "No confirmation code found in session."}, status=status.HTTP_400_BAD_REQUEST)

        # Получаем текущего пользователя
        user = request.user
        print(user)

        # Сравниваем введенный код с тем, что есть в сессии
        if user_code == request.session['confirmation_code']:
            user.is_confirmed = True
            user.save()

            # Удалить код после подтверждения (необязательно)
            del request.session['confirmation_code']

            return Response({"message": "Email confirmed successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid confirmation code."}, status=status.HTTP_400_BAD_REQUEST)

