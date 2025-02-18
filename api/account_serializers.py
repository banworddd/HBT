from rest_framework import serializers

from users.models import CustomUser

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True)


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, data):
        # Проверка на совпадение паролей
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Passwords don't match."})

        # Проверка на уникальность username
        if CustomUser.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})

        return data

    def create(self, validated_data):
        # Убираем второй пароль перед сохранением
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user