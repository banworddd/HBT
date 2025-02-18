from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from users.models import CustomUser


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError(
                {"detail": "Неправильное имя пользователя или пароль"}
            )

        if not user.is_confirmed:
            raise serializers.ValidationError(
                {"detail": "E-mail не подтверждён"}
            )

        data['user'] = user
        return data


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password2": "Введенные пароли не совпадают"}
            )

        if CustomUser.objects.filter(username=f"@{data['username']}").exists():
            raise serializers.ValidationError(
                {"username": "Данное имя пользователя уже занято"}
            )

        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {"email": "Данный e-mail уже занят"}
            )

        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user